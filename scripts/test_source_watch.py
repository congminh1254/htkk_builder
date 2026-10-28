"""Offline source parser, transport, credential and fixed-private-publication tests."""
import base64,datetime,hashlib,importlib.util,json,pathlib,unittest,urllib.error
from unittest.mock import patch
from email.message import Message
s=importlib.util.spec_from_file_location('watch',pathlib.Path(__file__).with_name('source-watch.py'));watch=importlib.util.module_from_spec(s);s.loader.exec_module(watch)
HTML=b'<table><tr><td>16/10/2026</td><td>HTKK <b>5.8.1</b></td><td><a class="linkDown" href="https://www.fshare.vn/file/TPW3FMLVAJL1%20">Download</a></td></tr></table>'
NOW='2026-10-25T12:00:00+00:00'
def good():return watch.observe(direct=lambda:(HTML,watch.PAGE),checked_at=NOW)
class Response:
 def __init__(self,body,url=watch.PAGE,status=200,content_type='text/html; charset=UTF-8',encoding=None):
  self.body=body;self.url=url;self.status=status;self.headers=Message();self.headers['Content-Type']=content_type
  if encoding:self.headers['Content-Encoding']=encoding
 def read(self,limit):return self.body[:limit]
 def __enter__(self):return self
 def __exit__(self,*args):pass
class Opener:
 def __init__(self,response):self.response=response;self.requests=[]
 def open(self,request,**kwargs):self.requests.append(request);return self.response
class ParserTests(unittest.TestCase):
 def test_known_row_normalizes_only_surrounding_space_and_does_not_activate(self):
  rows=watch.release_rows(HTML.decode());self.assertEqual(rows[0]['version'],'5.8.1');self.assertEqual(rows[0]['releaseDateAsPublished'],'16/10/2026');self.assertEqual(rows[0]['downloadReferences'],[{'recognition':'recognized-fshare','url':watch.PINNED_DOWNLOAD}]);self.assertFalse(watch.observation(rows)['automaticActivation']);self.assertFalse(watch.observation(rows)['compatibilityVerified'])
 def test_preserves_source_row_order_instead_of_sorting_versions_or_inferring_legal_effect(self):
  old=HTML.replace(b'5.8.1',b'5.7.9');new=HTML.replace(b'5.8.1',b'5.8.2');rows=watch.release_rows((old+new).decode());self.assertEqual([r['version']for r in rows],['5.7.9','5.8.2']);self.assertTrue(watch.observation(rows)['releaseChangedFromPinned'])
 def test_detects_version_and_same_version_link_drift_without_fetching_targets(self):
  for body in [HTML.replace(b'5.8.1',b'5.8.2'),HTML.replace(b'TPW3FMLVAJL1',b'NEWPUBLICID12'),HTML.replace(b'www.fshare.vn',b'unknown.example')]:
   report=watch.observe(direct=lambda:(body,watch.PAGE),checked_at=NOW);self.assertEqual(report['result'],'review-required');watch.validate_report(report)
 def test_drops_credential_private_script_query_and_unknown_link_values_from_reports(self):
  for url in ['https://user:PRIVATE@www.fshare.vn/file/TPW3FMLVAJL1','http://127.0.0.1/PRIVATE','javascript:PRIVATE','https://www.fshare.vn/file/TPW3FMLVAJL1?token=PRIVATE','https://unknown.example/PRIVATE']:
   body=HTML.decode().replace('https://www.fshare.vn/file/TPW3FMLVAJL1%20',url);report=watch.observe(direct=lambda:(body.encode(),watch.PAGE),checked_at=NOW);self.assertNotIn('PRIVATE',json.dumps(report));self.assertEqual(report['result'],'review-required')
 def test_rejects_missing_malformed_ambiguous_dates_versions_and_bounded_rows(self):
  bad=['<html>Login page</html>',HTML.decode().replace('16/10/2026','31/02/2026'),HTML.decode().replace('5.8.1','5.8.1 5.8.2'),HTML.decode().replace('16/10/2026','16/10/2026 17/10/2026'),'<tr><tr></tr></tr>','<tr>unclosed','<tr>'+('x'*8193)+'</tr>','<tr></tr>'*301]
  for html in bad:
   with self.subTest(length=len(html)),self.assertRaises(watch.SourceError):watch.release_rows(html)
 def test_ignores_script_text_and_limits_release_reports_to_twelve(self):
  row=HTML.decode().replace('<b>5.8.1</b>','<b>5.8.1</b><script>9.9.9 01/01/2020 SECRET</script>');self.assertEqual(watch.release_rows(row)[0]['version'],'5.8.1');self.assertEqual(len(watch.release_rows(HTML.decode()*13)),12)
 def test_changed_download_class_cannot_hide_a_new_release_before_an_old_pinned_row(self):
  changed=HTML.replace(b'5.8.1',b'5.8.2').replace(b'linkDown',b'new-download-class')
  with self.assertRaises(watch.SourceError):watch.release_rows((changed+HTML).decode())
 def test_release_version_normalization_retains_published_spelling(self):
  rows=watch.release_rows(HTML.decode().replace('5.8.1','005.08.001'));self.assertEqual(rows[0]['versionAsPublished'],'005.08.001');self.assertEqual(rows[0]['version'],'5.8.1');self.assertFalse(watch.observation(rows)['releaseChangedFromPinned'])
class TransportTests(unittest.TestCase):
 def test_direct_request_has_no_credentials_and_no_installer_request(self):
  opener=Opener(Response(HTML))
  with patch.object(watch.urllib.request,'build_opener',return_value=opener),patch.dict(watch.os.environ,{'SOURCE_PUBLISH_TOKEN':'PRIVATE_TOKEN','AGENT_AUTH_TOKEN':'PRIVATE_RELAY'}):data,final=watch.direct_fetch()
  self.assertEqual(data,HTML);self.assertEqual(final,watch.PAGE);self.assertEqual(len(opener.requests),1);request=opener.requests[0];self.assertEqual(request.full_url,watch.PAGE);self.assertNotIn('authorization',str(request.headers).lower());self.assertNotIn('PRIVATE',str(request.headers))
 def test_direct_failure_uses_optional_relay_once_and_never_requires_a_new_secret(self):
  calls=[]
  def direct():calls.append('direct');raise watch.SourceError('HTTP_DENIED',403)
  def relay():calls.append('relay');return HTML,watch.PAGE
  report=watch.observe(direct=direct,relay=relay,checked_at=NOW);self.assertEqual(calls,['direct','relay']);self.assertEqual(report['result'],'unchanged');self.assertEqual(report['transport'],'authorized-relay');watch.validate_report(report)
  report=watch.observe(direct=direct,checked_at=NOW);self.assertEqual(report['result'],'unreachable');self.assertEqual(len(report['attempts']),1);watch.validate_report(report)
 def test_direct_success_never_calls_relay(self):
  with patch.object(watch,'relay_fetch',side_effect=AssertionError('Relay must not run')):report=watch.observe(direct=lambda:(HTML,watch.PAGE),relay=lambda:watch.relay_fetch('test-token'),checked_at=NOW)
  self.assertEqual(report['transport'],'direct-https')
 def test_redirects_are_https_official_hosts_only_and_bounded(self):
  handler=watch.OfficialRedirect();request=watch.urllib.request.Request(watch.PAGE)
  for url in ['http://www.gdt.gov.vn/','https://127.0.0.1/','https://user:pass@www.gdt.gov.vn/','https://attacker.example/','https://www.gdt.gov.vn:444/']:
   with self.assertRaises(watch.SourceError):watch.OfficialRedirect().redirect_request(request,None,302,'',{},url)
  handler.count=5
  with self.assertRaises(watch.SourceError):handler.redirect_request(request,None,302,'',{},'https://www.gdt.gov.vn/')
 def test_relay_uses_only_fixed_endpoint_and_validates_base64_status_truncation_and_final_host(self):
  envelope={'status':200,'truncated':False,'url':watch.PAGE,'bodyEncoding':'base64','body':base64.b64encode(HTML).decode(),'headers':{'content-type':'text/html; charset=UTF-8','set-cookie':['PRIVATE_COOKIE']}}
  opener=Opener(Response(json.dumps(envelope).encode(),url=watch.RELAY,content_type='application/json'))
  with patch.object(watch.urllib.request,'build_opener',return_value=opener):self.assertEqual(watch.relay_fetch('test-only-token')[0],HTML)
  self.assertEqual(opener.requests[0].full_url,watch.RELAY);self.assertEqual(opener.requests[0].get_header('Authorization'),'Bearer test-only-token');self.assertIn('HTKK',opener.requests[0].get_header('User-agent'))
  for change in [{'status':403},{'truncated':True},{'bodyEncoding':'bad'},{'url':'https://attacker.example/'},{'body':'invalid-base64!'}]:
   bad=Opener(Response(json.dumps(dict(envelope,**change)).encode()))
   with patch.object(watch.urllib.request,'build_opener',return_value=bad),self.assertRaises(watch.SourceError):watch.relay_fetch('test-only-token')
   self.assertEqual(len(bad.requests),1)
 def test_relay_auth_error_is_not_retried_or_logged(self):
  calls=[]
  class Denied:
   def open(self,request,**kwargs):calls.append(request);raise urllib.error.HTTPError(watch.RELAY,403,'PRIVATE_TOKEN',{},None)
  with patch.object(watch.urllib.request,'build_opener',return_value=Denied()),self.assertRaises(watch.SourceError) as rejected:watch.relay_fetch('test-only-token')
  self.assertEqual(str(rejected.exception),'RELAY_AUTH');self.assertEqual(len(calls),1)
 def test_oversize_nonhtml_or_invalid_encoding_is_fail_closed(self):
  for response in [Response(b'x'*(watch.MAX_HTML+1)),Response(HTML,content_type='application/octet-stream'),Response(HTML,encoding='gzip')]:
   with patch.object(watch.urllib.request,'build_opener',return_value=Opener(response)),self.assertRaises(watch.SourceError):watch.direct_fetch()
  report=watch.observe(direct=lambda:(b'\xff',watch.PAGE),checked_at=NOW);self.assertEqual(report['result'],'invalid');self.assertEqual(report['failureCode'],'UTF8');watch.validate_report(report)
class ReportTests(unittest.TestCase):
 def test_report_is_exact_bounded_metadata_with_no_raw_html_or_response_headers(self):
  report=watch.validate_report(good());text=json.dumps(report);self.assertNotIn('<table>',text);self.assertNotIn('headers',report);self.assertEqual(report['body']['sha256'],hashlib.sha256(HTML).hexdigest());self.assertEqual(report['body']['bytes'],len(HTML))
  for change in [{'html':'PRIVATE'},{'scope':'full-runtime-verified'},{'failureCode':'PRIVATE'},{'body':{'sha256':'0'*64,'bytes':watch.MAX_HTML+1}},{'observation':dict(report['observation'],automaticActivation=True)},{'observation':dict(report['observation'],automaticActivation=0)},{'attempts':[dict(report['attempts'][0],errorCode='HTML_PARSE')]}]:
   with self.assertRaises((ValueError,TypeError)):watch.validate_report(dict(report,**change))
 def test_empty_or_tampered_success_and_foreign_reference_cannot_be_published(self):
  report=good();report['releases'][0]['downloadReferences'][0]['url']='https://attacker.example/PRIVATE'
  with patch.object(watch,'api') as api,self.assertRaises(ValueError):watch.publish(report,'test-token','test-status','42','a'*40)
  api.assert_not_called()
 def test_public_or_wrong_repo_is_denied_before_any_mutation(self):
  for info in [{'private':False,'full_name':watch.REPO},{'private':True,'full_name':'attacker/repo'}]:
   with patch.object(watch,'api',return_value=info) as api,self.assertRaises(ValueError):watch.publish(good(),'test-token','test-status','42','a'*40)
   api.assert_called_once_with('','test-token')
 def test_private_orphan_report_branch_and_status_are_fixed_and_do_not_write_main_or_pages(self):
  calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,token,payload,method))
   if path=='':return {'private':True,'full_name':watch.REPO}
   if path=='/branches/main':return {'commit':{'sha':'b'*40}}
   return {'sha':'c'*40}
  with patch.object(watch,'api',api):commit=watch.publish(good(),'test-token','test-status','42','a'*40,'b'*40)
  self.assertEqual(commit,'c'*40);self.assertEqual(calls[-2],('/git/refs/heads/official-source-observations','test-token',{'sha':'c'*40,'force':True},'PATCH'))
  payload=next(payload for path,_,payload,_ in calls if path=='/git/commits');self.assertEqual(payload['parents'],[])
  blob=next(payload for path,_,payload,_ in calls if path=='/git/blobs');private=json.loads(base64.b64decode(blob['content']));self.assertEqual(private['sourceSha'],'b'*40);self.assertEqual(private['report']['result'],'unchanged')
  self.assertEqual(calls[-1][0],'/statuses/'+'b'*40);self.assertEqual(calls[-1][1],'test-status');self.assertEqual(calls[-1][2]['context'],'htkk-source-watch');self.assertEqual(calls[-1][2]['state'],'success')
  self.assertFalse(any(path in ('/git/refs/heads/main','/git/refs/heads/pages-output') for path,_,_,_ in calls))
 def test_drift_and_unreachable_have_distinct_statuses_and_stale_dispatch_never_writes(self):
  for result,state in [('review-required','failure'),('unreachable','error')]:
   report=watch.observe(direct=lambda:(HTML.replace(b'5.8.1',b'5.8.2'),watch.PAGE),checked_at=NOW) if result=='review-required' else watch.observe(direct=lambda:(_ for _ in ()).throw(watch.SourceError('HTTP_DENIED',403)),checked_at=NOW)
   calls=[]
   def api(path,token,payload=None,method=None):
    calls.append((path,payload))
    if path=='':return {'private':True,'full_name':watch.REPO}
    if path=='/branches/main':return {'commit':{'sha':'b'*40}}
    return {'sha':'c'*40}
   with patch.object(watch,'api',api):watch.publish(report,'test-token','test-status','42','a'*40)
   self.assertEqual(calls[-1][1]['state'],state)
   calls.clear()
   with patch.object(watch,'api',api),self.assertRaises(ValueError):watch.publish(report,'test-token','test-status','42','a'*40,'d'*40)
   self.assertEqual(len(calls),2)
if __name__=='__main__':unittest.main()
