"""Offline behavioral regressions for inert source candidate downloads."""
import base64
import hashlib
import importlib.util
import io
import json
import pathlib
import socket
import ssl
import tempfile
import unittest
import urllib.error
from email.message import Message
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('candidate', pathlib.Path(__file__).with_name('source-candidate.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
URL = 'https://www.fshare.vn/file/TPW3FMLVAJL1'
CDN = 'https://download802.fshare.vn/dl/opaque-public-route/HTKK_5.8.1_DLL_signed.rar'
DATA = b'Rar!\x1a\x07\x01\x00' + b'archive-fixture-bytes' * 30
ETAG = '"test-entity-1"'
TOKEN = 'test-only-relay-credential'


def headers(**values):
    result = Message()
    for key, value in values.items():
        result[key.replace('_', '-')] = str(value)
    return result


class Response:
    def __init__(self, body, url=URL, status=200, extra=None):
        self.stream = io.BytesIO(body)
        self.url, self.status = url, status
        self.headers = headers(Content_Type='application/octet-stream', Content_Length=len(body))
        if extra:
            for key, value in extra.items():
                if key in self.headers:
                    del self.headers[key]
                self.headers[key] = value

    def read(self, limit):
        return self.stream.read(limit)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Openers:
    def __init__(self, responses, on_open=None):
        self.responses = list(responses)
        self.requests, self.handlers = [], []
        self.on_open = on_open

    def factory(self, handler):
        self.handlers.append(handler)
        return self

    def open(self, request, **kwargs):
        self.requests.append(request)
        if self.on_open:
            self.on_open(request)
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


def envelope(data=b'', url=URL, status=200, fields=None, response_headers=None):
    result = {'status': status, 'statusText': 'test-only', 'url': url, 'redirected': False, 'headers': response_headers or {}, 'body': base64.b64encode(data).decode(), 'bodyEncoding': 'base64', 'truncated': False}
    if fields:
        result.update(fields)
    return Response(json.dumps(result).encode(), url=c.RELAY, extra={'Content-Type': 'application/json'})


def relay_responses(data=DATA, etag=ETAG):
    meta = {'content-type': 'application/octet-stream', 'content-length': str(len(data)), 'etag': etag, 'last-modified': 'Wed, 28 Oct 2026 00:00:00 GMT'}
    responses = [envelope(response_headers=meta)]
    for start in range(0, len(data), c.RANGE_BYTES):
        end = min(start + c.RANGE_BYTES, len(data)) - 1
        part = {'content-type': 'application/octet-stream', 'content-length': str(end - start + 1), 'content-range': f'bytes {start}-{end}/{len(data)}', 'etag': etag}
        responses.append(envelope(data[start:end + 1], status=206, response_headers=part))
    return responses


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='candidate-offline-')
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.destination = self.root / 'candidate.rar'

    def fetch(self, responses, **kwargs):
        self.openers = Openers(responses)
        return c.fetch_resource(URL, self.destination, opener_factory=self.openers.factory, **kwargs)

    def no_files(self):
        self.assertEqual(list(self.root.iterdir()), [])

    def test_direct_stream_pins_hash_size_and_keeps_candidate_not_ready(self):
        digest = hashlib.sha256(DATA).hexdigest()
        r = self.fetch([Response(DATA)], expected_sha256=digest)
        self.assertEqual(self.destination.read_bytes(), DATA)
        self.assertEqual((r['sha256'], r['bytes'], r['kind']), (digest, len(DATA), 'rar'))
        self.assertTrue(r['expectedHashMatched'])
        for key in ('ready', 'automaticActivation', 'signatureVerified', 'payloadVerified'):
            self.assertIs(r[key], False)
        self.assertEqual(len(r['attempts']), 1)
        self.assertNotIn('Authorization', self.openers.requests[0].headers)
        self.assertNotIn(TOKEN, json.dumps(r))

    def test_unknown_hash_candidate_is_inert_and_metadata_drops_opaque_route(self):
        r = self.fetch([Response(DATA, url=CDN)])
        self.assertFalse(r['expectedHashMatched'])
        self.assertEqual(r['finalHost'], 'download802.fshare.vn')
        self.assertNotIn('opaque-public-route', json.dumps(r))
        self.assertNotIn('finalUrl', r)

    def test_url_policy_rejects_credentials_private_hosts_unsafe_redirects_and_unknown_mirrors(self):
        for url in ['http://www.gdt.gov.vn/x.zip', 'https://127.0.0.1/a.zip', 'https://[::1]/a.zip', 'https://www.gdt.gov.vn:444/a', 'https://u:p@www.fshare.vn/file/ABCDEFGH', 'https://download802.fshare.vn/dl/a.rar?token=private', 'https://fa.getpedia.net/data?q=private', 'https://download802.fshare.vn/other/a.rar', 'https://evil.fshare.vn/dl/a.rar', 'https://www.gdt.gov.vn/a\nInjected:private', 'https://www.gdt.gov.vn/a\\x', 'https://www.gdt.gov.vn/x#fragment']:
            with self.subTest(url=url), self.assertRaises(c.CandidateError) as error:
                c.allowed_url(url)
            self.assertEqual(error.exception.code, 'URL_POLICY')
        self.no_files()

    def test_direct_redirect_is_bounded_and_rebuilds_public_headers_only(self):
        handler = c.CandidateRedirect()
        req = c.urllib.request.Request(URL, headers={'Authorization': TOKEN, 'Cookie': 'test-only-cookie'})
        new = handler.redirect_request(req, None, 302, '', {}, CDN)
        self.assertEqual(new.full_url, CDN)
        self.assertNotIn('Authorization', new.headers)
        self.assertNotIn('Cookie', new.headers)
        self.assertNotIn('opaque-public-route', json.dumps(handler.trace))
        with self.assertRaises(c.CandidateError):
            handler.redirect_request(req, None, 302, '', {}, 'https://attacker.example/payload')
        handler.trace = [{}] * c.MAX_REDIRECTS
        with self.assertRaises(c.CandidateError):
            handler.redirect_request(req, None, 302, '', {}, CDN)

    def test_nonbinary_malformed_archive_encoding_and_lengths_fail_and_remove_partials(self):
        cases = [(Response(DATA, extra={'Content-Type': 'text/html'}), 'CONTENT_TYPE'), (Response(b'<html>fake archive</html>'), 'ARCHIVE_FORMAT'), (Response(DATA, extra={'Content-Encoding': 'gzip'}), 'CONTENT_ENCODING'), (Response(DATA, extra={'Content-Length': str(len(DATA) + 1)}), 'SIZE'), (Response(DATA, extra={'Content-Length': '-1'}), 'SIZE'), (Response(DATA, extra={'Content-Length': '0'}), 'SIZE')]
        for response, code in cases:
            with self.subTest(code=code), self.assertRaises(c.CandidateError) as error:
                self.fetch([response])
            self.assertEqual(error.exception.code, code)
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_streaming_size_bound_and_hash_mismatch_are_not_retried(self):
        for kwargs, code in [({'max_bytes': 16}, 'SIZE'), ({'expected_sha256': '0' * 64}, 'HASH')]:
            with self.assertRaises(c.CandidateError) as error:
                self.fetch([Response(DATA)], **kwargs)
            self.assertEqual(error.exception.code, code)
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_auth_tls_404_dns_unknown_and_tool_failures_never_retry(self):
        failures = [(urllib.error.HTTPError(URL, x, 'private', {}, None), 'HTTP_DENIED' if x in (401, 403) else 'HTTP_STATUS') for x in (401, 403, 404)]
        failures += [(urllib.error.URLError(ssl.SSLCertVerificationError('private')), 'TLS'), (socket.gaierror(socket.EAI_NONAME, 'private'), 'NETWORK'), (urllib.error.URLError('private unknown'), 'NETWORK'), (ValueError('private'), 'INTERNAL')]
        for failure, code in failures:
            with self.subTest(code=code), self.assertRaises(c.CandidateError) as error:
                self.fetch([failure])
            self.assertEqual(error.exception.code, code)
            self.assertNotIn('private', str(error.exception))
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_only_typed_transients_retry_once_and_cleanup_before_retry(self):
        for failure in [urllib.error.HTTPError(URL, 503, 'private', {}, None), TimeoutError('private'), ConnectionResetError('private'), socket.gaierror(socket.EAI_AGAIN, 'private')]:
            opens = Openers([failure, Response(DATA)], on_open=lambda req: self.assertEqual(len(list(self.root.glob('.htkk-candidate-*'))), 1))
            r = c.fetch_resource(URL, self.destination, opener_factory=opens.factory)
            self.assertEqual([a['result'] for a in r['attempts']], ['failed', 'downloaded'])
            self.assertEqual(len(opens.requests), 2)
            self.destination.unlink()
        opens = Openers([TimeoutError('private'), TimeoutError('private')])
        with self.assertRaises(c.CandidateError) as error:
            c.fetch_resource(URL, self.destination, opener_factory=opens.factory)
        self.assertEqual(len(error.exception.attempts), 2)
        self.no_files()

    def test_explicit_one_attempt_budget_and_no_automatic_relay_fallback(self):
        with patch.object(c, 'relay_request', side_effect=AssertionError('No fallback')):
            with self.assertRaises(c.CandidateError) as error:
                self.fetch([TimeoutError('private')], relay_token=TOKEN, max_attempts=1)
        self.assertEqual(len(error.exception.attempts), 1)
        self.assertEqual(len(self.openers.requests), 1)

    def test_destination_existing_symlink_and_symlink_parent_are_preserved(self):
        self.destination.write_bytes(b'existing')
        with self.assertRaises(c.CandidateError):
            self.fetch([Response(DATA)])
        self.assertEqual(self.destination.read_bytes(), b'existing')
        self.destination.unlink()
        outside = self.root / 'outside'
        outside.mkdir()
        link = self.root / 'link'
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('Symlinks unavailable to this test account')
        with self.assertRaises(c.CandidateError):
            c.fetch_resource(URL, link / 'candidate', opener_factory=Openers([Response(DATA)]).factory)
        self.assertEqual(list(outside.iterdir()), [])

    def test_atomic_commit_never_overwrites_destination_created_during_download(self):
        opens = Openers([Response(DATA)], on_open=lambda req: self.destination.write_bytes(b'other-owner'))
        with self.assertRaises(c.CandidateError) as error:
            c.fetch_resource(URL, self.destination, opener_factory=opens.factory)
        self.assertEqual(error.exception.code, 'DESTINATION')
        self.assertEqual(self.destination.read_bytes(), b'other-owner')
        self.assertFalse(list(self.root.glob('.htkk-candidate-*')))

    def test_relay_range_stream_checks_entity_size_and_keeps_auth_on_fixed_endpoint(self):
        with patch.object(c, 'RANGE_BYTES', 32):
            opens = Openers(relay_responses())
            r = c.fetch_resource(URL, self.destination, relay_token=TOKEN, transport='relay', opener_factory=opens.factory)
        self.assertEqual(self.destination.read_bytes(), DATA)
        self.assertGreater(r['rangeRequests'], 1)
        self.assertEqual(r['lastModified'], '2026-10-28T00:00:00+00:00')
        for req in opens.requests:
            self.assertEqual(req.full_url, c.RELAY)
            self.assertEqual(req.get_header('Authorization'), 'Bearer ' + TOKEN)
            self.assertIn('HTKK', req.get_header('User-agent'))
            payload = json.loads(req.data)
            self.assertNotIn(TOKEN, req.data.decode())
            self.assertFalse(payload['followRedirects'])
            self.assertEqual(payload['responseEncoding'], 'base64')
            self.assertNotIn('Authorization', payload['headers'])
        self.assertEqual(json.loads(opens.requests[0].data)['method'], 'HEAD')
        self.assertEqual(json.loads(opens.requests[1].data)['headers']['Range'], 'bytes=0-31')
        self.assertFalse(r['ready'])

    def test_relay_missing_or_weak_validator_fails_before_any_range(self):
        for etag in (None, 'W/"weak"', 'unquoted'):
            responses = relay_responses(etag=etag)
            if etag is None:
                env = json.loads(responses[0].stream.getvalue())
                env['headers'].pop('etag')
                responses[0] = Response(json.dumps(env).encode())
            with self.assertRaises(c.CandidateError) as error:
                self.fetch(responses, transport='relay', relay_token=TOKEN)
            self.assertEqual(error.exception.code, 'RANGE_VALIDATOR')
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_relay_rejects_range_gaps_wrong_totals_moving_entities_and_ignored_ranges(self):
        for field, value, code in [('content-range', 'bytes 1-8/999', 'RANGE'), ('etag', '"changed"', 'RANGE_VALIDATOR'), ('content-length', '999', 'RANGE')]:
            responses = relay_responses()
            env = json.loads(responses[1].stream.getvalue())
            env['headers'][field] = value
            responses[1] = Response(json.dumps(env).encode())
            with self.subTest(field=field), self.assertRaises(c.CandidateError) as error:
                self.fetch(responses, transport='relay', relay_token=TOKEN)
            self.assertEqual(error.exception.code, code)
            self.no_files()
        responses = relay_responses()
        env = json.loads(responses[1].stream.getvalue()); env['status'] = 200
        responses[1] = Response(json.dumps(env).encode())
        with self.assertRaises(c.CandidateError) as error:
            self.fetch(responses, transport='relay', relay_token=TOKEN)
        self.assertEqual(error.exception.code, 'RANGE_VALIDATOR')
        self.no_files()

    def test_relay_envelope_upstream_status_and_truncation_are_not_transport_success(self):
        changes = [({'status': 403}, 'HTTP_DENIED'), ({'status': '200'}, 'RELAY_ENVELOPE'), ({'truncated': True}, 'RELAY_TRUNCATED'), ({'bodyEncoding': 'bad'}, 'RELAY_ENVELOPE'), ({'body': '!not-base64'}, 'RELAY_ENVELOPE'), ({'url': 'https://attacker.example/a'}, 'URL_POLICY'), ({'redirected': True}, 'REDIRECT')]
        for change, code in changes:
            with self.subTest(change=change), self.assertRaises(c.CandidateError) as error:
                self.fetch([envelope(fields=change)], transport='relay', relay_token=TOKEN)
            self.assertEqual(error.exception.code, code)
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_relay_auth_500_tls_cloudflare_and_unknown_unreachable_are_not_retried(self):
        failures = [(urllib.error.HTTPError(c.RELAY, 401, 'private', {}, io.BytesIO(b'{}')), 'RELAY_AUTH'), (urllib.error.HTTPError(c.RELAY, 403, 'private', {}, io.BytesIO(b'{}')), 'RELAY_AUTH'), (urllib.error.HTTPError(c.RELAY, 500, 'private', {}, io.BytesIO(b'{}')), 'RELAY_HTTP'), (Response(b'error code: 1010'), 'RELAY_CLOUDFLARE')]
        for message, code in [('CERT_HAS_EXPIRED: private', 'TLS'), ('private unknown cause', 'NETWORK')]:
            body = json.dumps({'success': False, 'errorCode': 'UPSTREAM_UNREACHABLE', 'message': message}).encode()
            failures.append((urllib.error.HTTPError(c.RELAY, 424, 'private', {}, io.BytesIO(body)), code))
        for failure, code in failures:
            with self.subTest(code=code), self.assertRaises(c.CandidateError) as error:
                self.fetch([failure], transport='relay', relay_token=TOKEN)
            self.assertEqual(error.exception.code, code)
            self.assertNotIn('private', str(error.exception))
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()

    def test_relay_typed_timeout_retries_resource_once_and_second_timeout_is_larger(self):
        timeout = json.dumps({'success': False, 'errorCode': 'UPSTREAM_TIMEOUT', 'message': 'private'}).encode()
        opens = Openers([urllib.error.HTTPError(c.RELAY, 424, 'private', {}, io.BytesIO(timeout)), *relay_responses()])
        r = c.fetch_resource(URL, self.destination, relay_token=TOKEN, transport='relay', opener_factory=opens.factory)
        self.assertEqual([a['result'] for a in r['attempts']], ['failed', 'downloaded'])
        self.assertEqual(json.loads(opens.requests[0].data)['timeoutMs'], 60000)
        self.assertEqual(json.loads(opens.requests[1].data)['timeoutMs'], 120000)

    def test_relay_manual_redirect_never_forwards_token_or_private_headers(self):
        response = envelope(status=302, response_headers={'location': CDN})
        meta = {'content-type': 'application/octet-stream', 'content-length': str(len(DATA)), 'etag': ETAG}
        opens = Openers([response, envelope(url=CDN, response_headers=meta)])
        _, _, _, final, trace = c.relay_follow(URL, 'HEAD', TOKEN, {'Cookie': 'private', 'If-Match': ETAG}, 60000, c.time.monotonic() + 10, opens.factory)
        self.assertEqual(final, CDN)
        self.assertEqual(len(trace), 1)
        payload = json.loads(opens.requests[1].data)
        self.assertNotIn('Cookie', payload['headers'])
        self.assertNotIn('If-Match', payload['headers'])
        self.assertNotIn(TOKEN, opens.requests[1].data.decode())
        self.assertNotIn('opaque-public-route', json.dumps(trace))

    def test_baseline_mirror_requires_exact_official_hash_and_pins_mirror_hash(self):
        for value in (None, '', '0' * 64, True):
            opens = Openers([Response(DATA, url=c.BASELINE_MIRROR_URL)])
            with self.assertRaises(c.CandidateError) as error:
                c.fetch_baseline_mirror(self.destination, value, opener_factory=opens.factory)
            self.assertEqual(error.exception.code, 'HASH')
            self.assertEqual(opens.requests, [])
        opens = Openers([Response(DATA, url=c.BASELINE_MIRROR_URL)])
        with self.assertRaises(c.CandidateError) as error:
            c.fetch_baseline_mirror(self.destination, c.BASELINE_OFFICIAL_SHA256, opener_factory=opens.factory)
        self.assertEqual(error.exception.code, 'HASH')
        self.no_files()
        with patch.object(c, 'BASELINE_MIRROR_SHA256', hashlib.sha256(DATA).hexdigest()):
            opens = Openers([Response(DATA, url=c.BASELINE_MIRROR_URL)])
            result = c.fetch_baseline_mirror(self.destination, c.BASELINE_OFFICIAL_SHA256, opener_factory=opens.factory)
        self.assertEqual(opens.requests[0].full_url, c.BASELINE_MIRROR_URL)
        self.assertFalse(result['ready'])
        self.assertTrue(result['expectedHashMatched'])
        self.assertIn('not-trusted', result['scope'])
        self.assertNotIn('q=', json.dumps(result))

    def test_baseline_mirror_redirect_cannot_widen_the_default_host_policy(self):
        opens = Openers([Response(DATA, url='https://fa.getpedia.net/other')])
        with self.assertRaises(c.CandidateError) as error:
            c.fetch_baseline_mirror(self.destination, c.BASELINE_OFFICIAL_SHA256, opener_factory=opens.factory)
        self.assertEqual(error.exception.code, 'URL_POLICY')
        self.no_files()
        opens = Openers([Response(DATA, url=c.BASELINE_MIRROR_URL)])
        with self.assertRaises(c.CandidateError):
            c.fetch_resource(c.BASELINE_MIRROR_URL, self.destination, opener_factory=opens.factory)
        self.assertEqual(opens.requests, [])

    def test_relay_unknown_http_denial_never_turns_into_retry_from_body_claim(self):
        body = json.dumps({'success': False, 'errorCode': 'UPSTREAM_TIMEOUT', 'message': 'private'}).encode()
        for status, expected in [(400, 'RELAY_HTTP'), (403, 'RELAY_AUTH'), (500, 'RELAY_HTTP')]:
            with self.assertRaises(c.CandidateError) as error:
                self.fetch([urllib.error.HTTPError(c.RELAY, status, 'private', {}, io.BytesIO(body))], transport='relay', relay_token=TOKEN)
            self.assertEqual(error.exception.code, expected)
            self.assertEqual(len(self.openers.requests), 1)
            self.no_files()
        with self.assertRaises(c.CandidateError) as error:
            self.fetch([urllib.error.HTTPError(c.RELAY, 403, 'private', {}, io.BytesIO(b'error code: 1010'))], transport='relay', relay_token=TOKEN)
        self.assertEqual(error.exception.code, 'RELAY_CLOUDFLARE')
        self.assertEqual(len(self.openers.requests), 1)

    def test_relay_exact_range_bound_rejects_extra_bytes_and_partial_failure_cleans_before_retry(self):
        responses = relay_responses()
        env = json.loads(responses[1].stream.getvalue())
        env['body'] = base64.b64encode(DATA + b'EXTRA').decode()
        responses[1] = Response(json.dumps(env).encode())
        with self.assertRaises(c.CandidateError) as error:
            self.fetch(responses, transport='relay', relay_token=TOKEN)
        self.assertEqual(error.exception.code, 'RANGE')
        self.no_files()
        with patch.object(c, 'RANGE_BYTES', 32):
            responses = relay_responses()
            first = responses[:2]
            timeout = json.dumps({'success': False, 'errorCode': 'UPSTREAM_TIMEOUT', 'message': 'private'}).encode()
            opens = Openers([*first, urllib.error.HTTPError(c.RELAY, 424, 'private', {}, io.BytesIO(timeout)), *relay_responses()])
            result = c.fetch_resource(URL, self.destination, transport='relay', relay_token=TOKEN, opener_factory=opens.factory)
        self.assertEqual(self.destination.read_bytes(), DATA)
        self.assertEqual(len(result['attempts']), 2)
        self.assertFalse(list(self.root.glob('.htkk-candidate-*')))

    def test_no_credential_no_relay_request_and_deadline_fail_closed(self):
        with self.assertRaises(c.CandidateError) as error:
            self.fetch([], transport='relay')
        self.assertEqual(error.exception.code, 'RELAY_AUTH')
        self.assertEqual(len(self.openers.requests), 0)
        self.no_files()
        with patch.object(c.time, 'monotonic', side_effect=[0, c.DEADLINE_SECONDS + 1]):
            with self.assertRaises(c.CandidateError) as error:
                self.fetch([Response(DATA)])
        self.assertEqual(error.exception.code, 'DEADLINE')
        self.no_files()


if __name__ == '__main__':
    unittest.main()
