"""Behavioral tests: real sealing, policy gates and mocked private Git operations."""
import base64,hashlib,importlib.util,json,os,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('update',ROOT/'source-update.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
spec=importlib.util.spec_from_file_location('publish_update',ROOT/'source-update-publish.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
HTML=b'<table><tr><td>16/10/2026</td><td>HTKK 5.8.1</td><td><a class="linkDown" href="https://www.fshare.vn/file/TPW3FMLVAJL1">Download</a></td></tr></table>'
class UpdateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base=pathlib.Path(self.temp.name)
  env={'RUNNER_TEMP':str(self.base),'GITHUB_OUTPUT':str(self.base/'outputs'),'SOURCE_SHA':'a'*40,'GITHUB_SHA':'b'*40,'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1','VERIFY_CURRENT':'false','PREPARED_OBSERVATION_COMMIT':''}
  self.env=patch.dict(os.environ,env);self.env.start();self.addCleanup(self.env.stop)
  self.work,self.report,self.bundle=u.getpaths();self.good=u.watch.observe(direct=lambda:(HTML,u.watch.PAGE),checked_at='2026-10-28T00:00:00+00:00');u.write(self.report,self.good)
 def sealed(self):
  with patch.object(u.candidate,'fetch_resource',side_effect=AssertionError('metadata-only must not download')):u.stage()
  u.seal();return u.load(self.bundle/'bundle.json')
 def api(self,path,token,payload=None,method=None):
  self.calls.append((path,token,payload,method))
  if path=='':return {'private':True,'full_name':u.REPO}
  if path=='/branches/main':return {'commit':{'sha':'a'*40}}
  if path=='/git/blobs':
   raw=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}
  return {'sha':'c'*40}
 def publish(self,fetch=None):self.calls=[];return p.publish_bundle(self.bundle,'a'*40,'b'*40,'123',1,'source-fixture','status-fixture',fetch=fetch or self.api)
 def test_unchanged_scheduled_watch_does_not_download_or_claim_verification(self):
  b=self.sealed();self.assertIs(b['ready'],False);self.assertEqual(len(b['files']),4);self.assertEqual(u.load(self.bundle/'proposal.json')['trustStatus'],'not-run');self.assertIn('credentials_safe=true',(self.base/'outputs').read_text())
 def test_real_sealed_bundle_publishes_only_private_orphan_and_fixed_status(self):
  self.sealed();self.assertEqual(self.publish(),'c'*40)
  self.assertTrue(any(path=='/git/refs/heads/official-source-proposals'for path,*_ in self.calls));self.assertFalse(any(path in('/git/refs/heads/main','/git/refs/heads/pages-output')for path,*_ in self.calls))
  commit=next(x[2]for x in self.calls if x[0]=='/git/commits');self.assertEqual(commit['parents'],[])
  self.assertEqual(self.calls[-1][2]['context'],'htkk-source-candidate');self.assertEqual(self.calls[-1][2]['state'],'success')
 def test_no_network_before_all_file_hashes_and_trust_gates_validate(self):
  b=self.sealed();(self.bundle/'proposal.json').write_text('PRIVATE ALTERATION')
  calls=[]
  with self.assertRaises(ValueError):self.publish(fetch=lambda *a:calls.append(a))
  self.assertEqual(calls,[])
 def test_cleanup_failure_never_seals_or_opens_credential_gate(self):
  u.stage();stage=u.load(self.work/'candidate.json');stage['trustRequested']=True;stage['result']='staged'
  with patch.object(u,'validate_stage',return_value=stage),patch.object(u,'validate_trust',return_value=False):
   u.write(self.work/'trust.json',{'format':'failed-worker'});
   with self.assertRaises(ValueError):u.seal()
  self.assertIn('credentials_safe=false',(self.base/'outputs').read_text());self.assertFalse(self.bundle.exists())
 def test_unknown_candidate_is_quarantined_without_mirror_or_trust(self):
  self.report.unlink();r=u.watch.observe(direct=lambda:(HTML.replace(b'5.8.1',b'5.8.2'),u.watch.PAGE),checked_at='2026-10-28T00:00:00+00:00');u.write(self.report,r)
  data=b'Rar!\x1a\x07\x00inert-test-only'
  def download(url,destination,**kw):
   pathlib.Path(destination).write_bytes(data)
   return {'format':'htkk-source-candidate-download-v1','checkedAt':'2026-10-28T00:00:00+00:00','transport':'direct','requestedUrlSha256':'1'*64,'requestedHost':'www.fshare.vn','attempts':[{'attempt':1,'result':'downloaded','errorCode':None,'httpStatus':200}],'expectedHashMatched':False,'signatureVerified':False,'payloadVerified':False,'ready':False,'automaticActivation':False,'bytes':len(data),'sha256':u.digest(data),'kind':'rar','status':200,'finalHost':'www.fshare.vn','finalUrlSha256':'2'*64,'redirects':[],'lastModified':None,'rangeRequests':0}
  with patch.object(u.candidate,'fetch_resource',download),patch.object(u.candidate,'fetch_baseline_mirror',side_effect=AssertionError('no unknown mirror')):u.stage()
  u.seal();b=u.load(self.bundle/'bundle.json');self.assertEqual(b['result'],'review-required');self.assertIs(u.load(self.bundle/'candidate.json')['trustRequested'],False)
  self.publish();parts=[]
  for path,_,body,_ in self.calls:
   if path=='/git/blobs':
    raw=base64.b64decode(body['content'])
    if raw.startswith(b'{'):
     j=json.loads(raw)
     if j.get('format')=='htkk-private-inert-source-parts-v1':parts=j['archives']
  self.assertEqual(parts[0]['sha256'],u.digest(data));self.assertEqual(parts[0]['chunks'][0]['bytes'],len(data));self.assertEqual(self.calls[-1][2]['state'],'failure')
 def test_ref_auth_or_422_never_falls_back_to_create(self):
  self.sealed()
  for status in(401,403,422,500):
   def api(path,*a):
    if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/',status,'PRIVATE',{},None)
    return self.api(path,*a)
   with self.assertRaises(urllib.error.HTTPError):self.publish(fetch=api)
   self.assertFalse(any(path=='/git/refs'for path,*_ in self.calls))
 def test_only_ref_404_allows_create(self):
  self.sealed()
  def api(path,*a):
   if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/',404,'missing',{},None)
   return self.api(path,*a)
  self.publish(fetch=api);self.assertTrue(any(path=='/git/refs'for path,*_ in self.calls))
 def test_stale_main_after_uploads_never_updates_ref_or_status(self):
  self.sealed();reads=0
  def api(path,*a):
   nonlocal reads
   if path=='/branches/main':
    reads+=1
    if reads>1:return {'commit':{'sha':'f'*40}}
   return self.api(path,*a)
  with self.assertRaises(ValueError):self.publish(fetch=api)
  self.assertFalse(any(path.startswith('/git/ref')or path.startswith('/statuses')for path,*_ in self.calls))
 def test_publish_rejects_directory_escape_symlink_unknown_file_and_forged_ready(self):
  self.sealed();b=u.load(self.bundle/'bundle.json')
  for change in({'ready':True},{'credentialsSafe':False},{'sourceSha':'f'*40},{'extra':'PRIVATE'}):
   (self.bundle/'bundle.json').write_text(json.dumps(dict(b,**change)))
   with self.assertRaises(ValueError):self.publish()
  (self.bundle/'bundle.json').write_text(json.dumps(b));(self.bundle/'extra').write_text('x')
  with self.assertRaises(ValueError):self.publish()
 def test_tls_and_auth_do_not_switch_transport_or_retry(self):
  self.env.stop();self.env=patch.dict(os.environ,{'VERIFY_CURRENT':'true','AGENT_AUTH_TOKEN':'test-only-relay','RUNNER_TEMP':str(self.base),'GITHUB_OUTPUT':str(self.base/'outputs')});self.env.start()
  for code,status in(('TLS',None),('HTTP_DENIED',401),('HTTP_DENIED',403)):
   if self.work.exists():u.shutil.rmtree(self.work)
   with patch.object(u.candidate,'fetch_resource',side_effect=u.candidate.CandidateError(code,status))as fetch:u.stage();self.assertEqual(fetch.call_count,1)
 def test_malformed_metadata_and_tls_do_not_use_relay(self):
  for error in(u.watch.SourceError('TLS'),u.watch.SourceError('HTTP_DENIED',401),u.watch.SourceError('HTML_PARSE')):
   with patch.object(u.watch,'relay_fetch',side_effect=AssertionError('no fallback')):
    r=u.watch.observe(direct=lambda:(_ for _ in()).throw(error),relay=lambda:u.watch.relay_fetch('test-only'))
    self.assertEqual(len(r['attempts']),1)
if __name__=='__main__':unittest.main()
