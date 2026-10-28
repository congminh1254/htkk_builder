"""Download a public HTKK candidate as inert bytes; never activate or extract it.

Only source-traced HTTPS GDT/Fshare routes are supported. Direct and relay are
explicit transports, so a caller cannot silently hide a TLS/auth failure by
changing transports. A successful download is NOT signature or payload trust.
"""
import base64
import datetime
import email.utils
import errno
import hashlib
import http.client
import ipaddress
import json
import os
import pathlib
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

RELAY = 'https://service.medpass.vn/api/agent/fetch'
USER_AGENT = 'HTKK-Source-Candidate/1.0'
BASELINE_OFFICIAL_SHA256 = '5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95'
BASELINE_MIRROR_SHA256 = '3f50ede214d802984549aa3841c3de6614fca90021ef5029a9c1ac1999776edb'
BASELINE_MIRROR_URL = 'https://fa.getpedia.net/data?q===QMzEDM2gjM3MDM0UzN4ITOzYDfxMTMxEDfwlmeuETL40SNts0SUh0L3EzLwEzL2IDMy8SZslmZvEGdhR2L'
MAX_BYTES = 256 * 1024 * 1024
RANGE_BYTES = 4 * 1024 * 1024
MAX_ENVELOPE = 6 * 1024 * 1024
MAX_REDIRECTS = 5
DEADLINE_SECONDS = 300
OFFICIAL_HOSTS = frozenset(('gdt.gov.vn', 'www.gdt.gov.vn', 'thuedientu.gdt.gov.vn'))
TRANSIENT_HTTP = frozenset((408, 429, 500, 502, 503, 504))
BINARY_TYPES = frozenset(('application/octet-stream', 'application/x-rar-compressed', 'application/vnd.rar', 'application/x-rar', 'application/zip', 'application/x-zip-compressed', 'application/x-msdownload', 'application/x-msi', 'application/vnd.ms-cab-compressed', 'application/x-7z-compressed'))
ERRORS = frozenset(('URL_POLICY', 'REDIRECT', 'HTTP_DENIED', 'HTTP_STATUS', 'TLS', 'TIMEOUT', 'NETWORK', 'CONTENT_TYPE', 'CONTENT_ENCODING', 'SIZE', 'HASH', 'ARCHIVE_FORMAT', 'DESTINATION', 'IO', 'RELAY_AUTH', 'RELAY_HTTP', 'RELAY_CLOUDFLARE', 'RELAY_ENVELOPE', 'RELAY_UPSTREAM', 'RELAY_TRUNCATED', 'RANGE', 'RANGE_VALIDATOR', 'DEADLINE', 'INTERNAL'))


class CandidateError(ValueError):
    def __init__(self, code, status=None, retryable=False, attempts=()):
        if code not in ERRORS:
            raise ValueError('Invalid candidate error code')
        self.code = code
        self.status = status if type(status) is int and 100 <= status <= 599 else None
        self.retryable = bool(retryable)
        self.attempts = tuple(attempts)
        super().__init__(code)


def allowed_url(url):
    """No arbitrary mirror, userinfo, unknown query parameters or private-IP routes."""
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 or ord(c) == 127 for c in url) or '\\' in url:
        raise CandidateError('URL_POLICY')
    try:
        p = urllib.parse.urlsplit(url)
        host = p.hostname
        if p.scheme != 'https' or not host or p.username or p.password or p.fragment or p.port not in (None, 443):
            raise CandidateError('URL_POLICY')
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise CandidateError('URL_POLICY')
        signed_query=False
        if p.query:
            try:
                items=urllib.parse.parse_qsl(p.query,keep_blank_values=True,strict_parsing=True)
                signed_query=len(items)==1 and items[0][0]=='token' and re.fullmatch(r'[A-Za-z0-9._~+/=\-]{1,1024}',items[0][1]) is not None
            except ValueError:pass
        if host in OFFICIAL_HOSTS:
            pass
        elif host in ('fshare.vn', 'www.fshare.vn'):
            if (p.query and not signed_query) or not re.fullmatch(r'/file/[A-Za-z0-9]{8,32}', p.path):
                raise CandidateError('URL_POLICY')
        elif re.fullmatch(r'download[0-9]{1,4}\.fshare\.vn', host):
            if (p.query and not signed_query) or not re.fullmatch(r'/dl/[A-Za-z0-9_./%+\-]{1,1800}', p.path):
                raise CandidateError('URL_POLICY')
        else:
            raise CandidateError('URL_POLICY')
        return url
    except CandidateError:
        raise
    except (TypeError, ValueError):
        raise CandidateError('URL_POLICY') from None


def host(url):
    return urllib.parse.urlsplit(url).hostname


def sha(data):
    return hashlib.sha256(data).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


class CandidateRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, url_validator=allowed_url):
        super().__init__()
        self.trace = []
        self.url_validator = url_validator

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if code not in (301, 302, 303, 307, 308) or len(self.trace) >= MAX_REDIRECTS:
            raise CandidateError('REDIRECT')
        self.url_validator(newurl)
        self.trace.append({'status': code, 'fromHost': host(request.full_url), 'toHost': host(newurl), 'urlSha256': sha(newurl.encode())})
        # Rebuild with only public request headers, including across origins.
        return urllib.request.Request(newurl, method=request.get_method(), headers={'User-Agent': USER_AGENT, 'Accept': 'application/octet-stream', 'Accept-Encoding': 'identity'})


def transport_error(error):
    if isinstance(error, CandidateError):
        return error
    if isinstance(error, urllib.error.HTTPError):
        return CandidateError('HTTP_DENIED' if error.code in (401, 403) else 'HTTP_STATUS', error.code, error.code in TRANSIENT_HTTP)
    if isinstance(error, urllib.error.URLError):
        return transport_error(error.reason) if isinstance(error.reason, BaseException) else CandidateError('NETWORK')
    if isinstance(error, ssl.SSLError):
        return CandidateError('TLS')
    if isinstance(error, (TimeoutError, socket.timeout)):
        return CandidateError('TIMEOUT', retryable=True)
    if isinstance(error, socket.gaierror):
        return CandidateError('NETWORK', retryable=error.errno == socket.EAI_AGAIN)
    if isinstance(error, (ConnectionResetError, ConnectionAbortedError, http.client.RemoteDisconnected)):
        return CandidateError('NETWORK', retryable=True)
    if isinstance(error, OSError):
        return CandidateError('NETWORK', retryable=error.errno in (errno.ECONNRESET, errno.ECONNABORTED, errno.ENETRESET))
    return CandidateError('INTERNAL')


def header(headers, name):
    if hasattr(headers, 'get_all'):
        values = headers.get_all(name, [])
        if len(values) > 1:
            raise CandidateError('RANGE')
        value = values[0] if values else None
    else:
        matches = [v for k, v in headers.items() if k.lower() == name.lower()]
        if len(matches) > 1:
            raise CandidateError('RANGE')
        value = matches[0] if matches else None
    if value is not None and (not isinstance(value, str) or len(value) > 2048 or '\r' in value or '\n' in value):
        raise CandidateError('RANGE')
    return value


def content_length(headers, maximum, required=False):
    raw = header(headers, 'content-length')
    if raw is None and not required:
        return None
    if not isinstance(raw, str) or not re.fullmatch(r'[0-9]{1,12}', raw):
        raise CandidateError('SIZE')
    size = int(raw)
    if not 1 <= size <= maximum:
        raise CandidateError('SIZE')
    return size


def validate_binary_headers(headers):
    value = header(headers, 'content-type')
    if not value or value.split(';', 1)[0].strip().lower() not in BINARY_TYPES:
        raise CandidateError('CONTENT_TYPE')
    if (header(headers, 'content-encoding') or 'identity').lower() not in ('', 'identity'):
        raise CandidateError('CONTENT_ENCODING')


def strong_etag(headers):
    value = header(headers, 'etag')
    if value is None or not re.fullmatch(r'"[\x21\x23-\x7e]{1,200}"', value):
        raise CandidateError('RANGE_VALIDATOR')
    return value


def modified_at(headers):
    raw = header(headers, 'last-modified')
    if raw is None:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(raw)
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(datetime.timezone.utc).isoformat(timespec='seconds')
    except (TypeError, ValueError, OverflowError):
        return None


def archive_kind(prefix):
    for magic, kind in ((b'Rar!\x1a\x07\x00', 'rar'), (b'Rar!\x1a\x07\x01\x00', 'rar'), (b'PK\x03\x04', 'zip'), (b'7z\xbc\xaf\x27\x1c', '7z'), (b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', 'compound'), (b'MSCF', 'cab'), (b'MZ', 'pe')):
        if prefix.startswith(magic):
            return kind
    raise CandidateError('ARCHIVE_FORMAT')


def check_deadline(deadline):
    if time.monotonic() > deadline:
        raise CandidateError('DEADLINE')


def stream_direct(url, output, maximum, deadline, opener_factory=None, url_validator=allowed_url):
    redirects = CandidateRedirect(url_validator)
    opener = opener_factory(redirects) if opener_factory else urllib.request.build_opener(redirects)
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/octet-stream', 'Accept-Encoding': 'identity'})
    try:
        with opener.open(request, timeout=30) as response:
            if response.status != 200:
                raise CandidateError('HTTP_DENIED' if response.status in (401, 403) else 'HTTP_STATUS', response.status, response.status in TRANSIENT_HTTP)
            final = url_validator(response.url)
            validate_binary_headers(response.headers)
            expected_size = content_length(response.headers, maximum)
            digest = hashlib.sha256()
            count = 0
            prefix = b''
            while True:
                check_deadline(deadline)
                block = response.read(min(65536, maximum - count + 1))
                check_deadline(deadline)
                if not isinstance(block, bytes):
                    raise CandidateError('IO')
                if not block:
                    break
                count += len(block)
                if count > maximum:
                    raise CandidateError('SIZE')
                prefix = (prefix + block)[:16]
                output.write(block)
                digest.update(block)
            if expected_size is not None and count != expected_size:
                raise CandidateError('SIZE')
            if not count:
                raise CandidateError('SIZE')
            return {'bytes': count, 'sha256': digest.hexdigest(), 'kind': archive_kind(prefix), 'status': 200, 'finalHost': host(final), 'finalUrlSha256': sha(final.encode()), 'redirects': redirects.trace, 'lastModified': modified_at(response.headers), 'rangeRequests': 0}
    except CandidateError:
        raise
    except Exception as error:
        raise transport_error(error) from None


def relay_error(envelope, relay_status):
    code = envelope.get('errorCode')
    if envelope.get('success') is not False or not isinstance(code, str):
        raise CandidateError('RELAY_ENVELOPE')
    if code == 'UPSTREAM_TIMEOUT':
        return CandidateError('TIMEOUT', retryable=True)
    if code == 'UPSTREAM_UNREACHABLE':
        message = envelope.get('message', '')
        if not isinstance(message, str):
            raise CandidateError('RELAY_ENVELOPE')
        if re.search(r'CERT_HAS_EXPIRED|CERT_NOT_YET_VALID|ERR_TLS_|UNABLE_TO_VERIFY|SELF_SIGNED|certificate|SSL|TLS', message, re.I):
            return CandidateError('TLS')
        transient = re.search(r'\b(?:ECONNRESET|ECONNABORTED|EAI_AGAIN|ETIMEDOUT)\b', message) is not None
        return CandidateError('NETWORK', retryable=transient)
    if code in ('REDIRECT_NOT_ALLOWED', 'TOO_MANY_REDIRECTS'):
        return CandidateError('REDIRECT')
    return CandidateError('RELAY_HTTP', relay_status)


def relay_request(url, method, token, request_headers, timeout_ms, opener_factory=None, url_validator=allowed_url):
    url_validator(url)
    if not isinstance(token, str) or not token:
        raise CandidateError('RELAY_AUTH')
    payload = {'url': url, 'method': method, 'headers': request_headers, 'timeoutMs': timeout_ms, 'followRedirects': False, 'responseEncoding': 'base64'}
    request = urllib.request.Request(RELAY, data=json.dumps(payload).encode(), headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'User-Agent': USER_AGENT}, method='POST')
    opener = opener_factory(NoRedirect()) if opener_factory else urllib.request.build_opener(NoRedirect())
    relay_status = 200
    try:
        with opener.open(request, timeout=timeout_ms / 1000 + 15) as response:
            relay_status = response.status
            raw = response.read(MAX_ENVELOPE + 1)
    except urllib.error.HTTPError as error:
        relay_status = error.code
        raw = error.read(MAX_ENVELOPE + 1)
    except Exception as error:
        raise transport_error(error) from None
    if len(raw) > MAX_ENVELOPE:
        raise CandidateError('SIZE')
    if re.fullmatch(rb'\s*error code: [0-9]{3,4}\s*', raw):
        raise CandidateError('RELAY_CLOUDFLARE', relay_status)
    if relay_status in (401, 403):
        raise CandidateError('RELAY_AUTH', relay_status)
    if relay_status not in (200, 424):
        raise CandidateError('RELAY_HTTP', relay_status)
    try:
        envelope = json.loads(raw)
        if not isinstance(envelope, dict):
            raise CandidateError('RELAY_ENVELOPE')
        if envelope.get('success') is False:
            raise relay_error(envelope, relay_status)
        if relay_status != 200 or type(envelope.get('status')) is not int or not 100 <= envelope['status'] <= 599:
            raise CandidateError('RELAY_ENVELOPE')
        if envelope.get('truncated') is not False:
            raise CandidateError('RELAY_TRUNCATED')
        if type(envelope.get('redirected')) is not bool or envelope['redirected'] is not False:
            # All redirects are handled explicitly and source-policy checked.
            raise CandidateError('REDIRECT')
        final = url_validator(envelope.get('url'))
        if final != url:
            raise CandidateError('REDIRECT')
        headers = envelope.get('headers')
        if not isinstance(headers, dict) or any(not isinstance(k, str) for k in headers):
            raise CandidateError('RELAY_ENVELOPE')
        safe_headers = {k: v for k, v in headers.items() if k.lower() in ('content-type', 'content-length', 'content-encoding', 'content-range', 'etag', 'last-modified', 'location')}
        if any(not isinstance(v, str) for v in safe_headers.values()):
            raise CandidateError('RELAY_ENVELOPE')
        body = envelope.get('body')
        if not isinstance(body, str) or envelope.get('bodyEncoding') not in ('base64', 'text'):
            raise CandidateError('RELAY_ENVELOPE')
        data = base64.b64decode(body, validate=True) if envelope['bodyEncoding'] == 'base64' else body.encode('utf-8')
        if len(data) > RANGE_BYTES:
            raise CandidateError('SIZE')
        return envelope['status'], safe_headers, data
    except CandidateError:
        raise
    except Exception:
        raise CandidateError('RELAY_ENVELOPE') from None


def relay_follow(url, method, token, headers, timeout_ms, deadline, opener_factory, url_validator=allowed_url):
    trace = []
    current = url
    while True:
        check_deadline(deadline)
        status, response_headers, body = relay_request(current, method, token, headers, timeout_ms, opener_factory, url_validator)
        check_deadline(deadline)
        if status not in (301, 302, 303, 307, 308):
            if status not in (200, 206):
                raise CandidateError('HTTP_DENIED' if status in (401, 403) else 'HTTP_STATUS', status, status in TRANSIENT_HTTP)
            return status, response_headers, body, current, trace
        if len(trace) >= MAX_REDIRECTS:
            raise CandidateError('REDIRECT')
        location = header(response_headers, 'location')
        if not location:
            raise CandidateError('REDIRECT')
        newurl = url_validator(urllib.parse.urljoin(current, location))
        trace.append({'status': status, 'fromHost': host(current), 'toHost': host(newurl), 'urlSha256': sha(newurl.encode())})
        if (urllib.parse.urlsplit(current).scheme, host(current), urllib.parse.urlsplit(current).port) != (urllib.parse.urlsplit(newurl).scheme, host(newurl), urllib.parse.urlsplit(newurl).port):
            allowed = {'accept', 'accept-language', 'cache-control', 'content-language', 'content-type', 'pragma', 'user-agent'}
            headers = {k: v for k, v in headers.items() if k.lower() in allowed}
        current = newurl


def stream_relay(url, output, maximum, deadline, token, timeout_ms, opener_factory=None, url_validator=allowed_url):
    status, headers, body, final, redirects = relay_follow(url, 'HEAD', token, {}, timeout_ms, deadline, opener_factory, url_validator)
    if status != 200 or body:
        raise CandidateError('RANGE')
    validate_binary_headers(headers)
    total = content_length(headers, maximum, required=True)
    etag = strong_etag(headers)
    digest = hashlib.sha256()
    count = 0
    prefix = b''
    requests = 0
    while count < total:
        end = min(count + RANGE_BYTES, total) - 1
        status, part_headers, data, part_final, trace = relay_follow(final, 'GET', token, {'Range': f'bytes={count}-{end}', 'If-Match': etag, 'Accept-Encoding': 'identity'}, timeout_ms, deadline, opener_factory, url_validator)
        # Do not mix bytes from a moving CDN route or a second entity.
        if status != 206 or part_final != final or trace or strong_etag(part_headers) != etag:
            raise CandidateError('RANGE_VALIDATOR')
        validate_binary_headers(part_headers)
        if header(part_headers, 'content-range') != f'bytes {count}-{end}/{total}' or content_length(part_headers, RANGE_BYTES, required=True) != end - count + 1 or len(data) != end - count + 1:
            raise CandidateError('RANGE')
        count += len(data)
        prefix = (prefix + data)[:16]
        output.write(data)
        digest.update(data)
        requests += 1
    return {'bytes': count, 'sha256': digest.hexdigest(), 'kind': archive_kind(prefix), 'status': 206, 'finalHost': host(final), 'finalUrlSha256': sha(final.encode()), 'redirects': redirects, 'lastModified': modified_at(headers), 'rangeRequests': requests}


def safe_destination(destination):
    path = pathlib.Path(destination).absolute()
    try:
        for parent in (path.parent, *path.parents):
            junction = getattr(parent, 'is_junction', lambda: False)()
            if parent.is_symlink() or junction or getattr(parent.stat(follow_symlinks=False), 'st_file_attributes', 0) & 0x400:
                raise CandidateError('DESTINATION')
    except OSError:
        raise CandidateError('DESTINATION') from None
    if not path.parent.is_dir() or os.path.lexists(path):
        raise CandidateError('DESTINATION')
    return path


def _fetch_resource(url, destination, expected_sha256=None, relay_token=None, transport='direct', max_bytes=MAX_BYTES, max_attempts=2, opener_factory=None, url_validator=allowed_url):
    """Write one candidate without execution; preserve only bounded, safe metadata.

    ``opener_factory`` is a network test adapter accepting the redirect handler.
    Retries restart the complete resource and remove its private partial file.
    No automatic cross-transport fallback is performed. Each relay request gets
    one call; max_attempts bounds the whole logical resource, not each chunk.
    """
    url_validator(url)
    if transport not in ('direct', 'relay') or type(max_bytes) is not int or not 1 <= max_bytes <= MAX_BYTES or type(max_attempts) is not int or not 1 <= max_attempts <= 2:
        raise CandidateError('INTERNAL')
    if expected_sha256 is not None and (not isinstance(expected_sha256, str) or not re.fullmatch('[a-f0-9]{64}', expected_sha256)):
        raise CandidateError('HASH')
    path = safe_destination(destination)
    attempts = []
    for number in range(1, max_attempts + 1):
        partial = path.parent / ('.htkk-candidate-' + uuid.uuid4().hex + '.part')
        try:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
            with os.fdopen(os.open(partial, flags, 0o600), 'wb') as output:
                deadline = time.monotonic() + DEADLINE_SECONDS
                result = stream_direct(url, output, max_bytes, deadline, opener_factory, url_validator) if transport == 'direct' else stream_relay(url, output, max_bytes, deadline, relay_token, 60000 if number == 1 else 120000, opener_factory, url_validator)
            if expected_sha256 is not None and result['sha256'] != expected_sha256:
                raise CandidateError('HASH')
            # Atomic no-overwrite publication; do not replace somebody else's file.
            os.link(partial, path, follow_symlinks=False)
            partial.unlink()
            attempts.append({'attempt': number, 'result': 'downloaded', 'errorCode': None, 'httpStatus': result['status']})
            return {'format': 'htkk-source-candidate-download-v1', 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'transport': transport, 'requestedUrlSha256': sha(url.encode()), 'requestedHost': host(url), 'attempts': attempts, 'expectedHashMatched': expected_sha256 is not None, 'signatureVerified': False, 'payloadVerified': False, 'ready': False, 'automaticActivation': False, **result}
        except Exception as error:
            try:
                partial.unlink(missing_ok=True)
            except OSError:
                raise CandidateError('IO', attempts=attempts) from None
            error = error if isinstance(error, CandidateError) else CandidateError('DESTINATION' if isinstance(error, FileExistsError) else 'IO')
            attempts.append({'attempt': number, 'result': 'failed', 'errorCode': error.code, 'httpStatus': error.status})
            if not error.retryable or number == max_attempts:
                raise CandidateError(error.code, error.status, error.retryable, attempts) from None
    raise CandidateError('INTERNAL')


def fetch_resource(url, destination, expected_sha256=None, relay_token=None, transport='direct', max_bytes=MAX_BYTES, max_attempts=2, opener_factory=None):
    """Download only source-traced GDT/Fshare URLs as inert candidate bytes."""
    return _fetch_resource(url, destination, expected_sha256, relay_token, transport, max_bytes, max_attempts, opener_factory)


def fetch_baseline_mirror(destination, official_sha256, relay_token=None, transport='direct', max_attempts=2, opener_factory=None):
    """Fetch ONE historical mirror only after matching the official archive hash.

    This does not assert mirror trust. A separate verifier must establish matching
    CAB bytes and signed MSI/setup/payload before using these mirrored files.
    No new version, arbitrary mirror URL or redirect is authorized by this helper.
    """
    if official_sha256 != BASELINE_OFFICIAL_SHA256:
        raise CandidateError('HASH')
    def exact_mirror(url):
        if url != BASELINE_MIRROR_URL:
            raise CandidateError('URL_POLICY')
        return url
    result = _fetch_resource(BASELINE_MIRROR_URL, destination, BASELINE_MIRROR_SHA256, relay_token, transport, MAX_BYTES, max_attempts, opener_factory, exact_mirror)
    result['scope'] = 'baseline-mirror-not-trusted-until-cab-and-signature-chain-match'
    return result
