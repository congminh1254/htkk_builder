"""Observe fixed public GDT HTML only. Never follow installer links or activate code.

Observation has no GitHub credential. Publication is a separate trusted process.
"""
import argparse,base64,datetime,hashlib,json,os,pathlib,re,socket,ssl,urllib.error,urllib.parse,urllib.request
from html.parser import HTMLParser
PAGE='https://www.gdt.gov.vn/wps/portal/home/hotrokekhai?1dmy&current=true&urile=wcm:path:/gdt+content/sa_gdt/htkk/soft_sup_declare'
PINNED_VERSION='5.8.1'
PINNED_DOWNLOAD='https://www.fshare.vn/file/TPW3FMLVAJL1'
RELAY='https://service.medpass.vn/api/agent/fetch'
REPO='congminh1254/htkk_web';BUILDER='congminh1254/htkk_builder';BRANCH='official-source-observations'
MAX_HTML=2_000_000;MAX_REPORT=64_000
HOSTS=('www.gdt.gov.vn','gdt.gov.vn')
ERRORS=frozenset(('HTTP_DENIED','HTTP_STATUS','TLS','TIMEOUT','NETWORK','REDIRECT','TOO_LARGE','CONTENT_TYPE','CONTENT_ENCODING','UTF8','HTML_PARSE','NO_RELEASES','RELAY_AUTH','RELAY_HTTP','RELAY_UPSTREAM','RELAY_ENVELOPE','INTERNAL'))
class SourceError(ValueError):
 def __init__(self,code,status=None):
  if code not in ERRORS:raise ValueError('Invalid safe source error')
  self.code=code;self.status=status if type(status) is int and 100<=status<=599 else None
  super().__init__(code)

def official_url(url):
 try:p=urllib.parse.urlsplit(url);valid=isinstance(url,str) and not any(ord(c)<=32 or ord(c)==127 for c in url) and not p.fragment and p.scheme=='https' and p.hostname in HOSTS and not p.username and not p.password and p.port in (None,443) and len(url)<=2048
 except (TypeError,ValueError):valid=False
 if not valid:raise SourceError('REDIRECT')
 return url

class OfficialRedirect(urllib.request.HTTPRedirectHandler):
 def __init__(self):super().__init__();self.count=0
 def redirect_request(self,request,fp,code,msg,headers,newurl):
  self.count+=1
  if self.count>5:raise SourceError('REDIRECT')
  official_url(newurl)
  return super().redirect_request(request,fp,code,msg,headers,newurl)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None

def transport_error(error):
 if isinstance(error,urllib.error.HTTPError):return SourceError('HTTP_DENIED' if error.code in (401,403) else 'HTTP_STATUS',error.code)
 if isinstance(error,(TimeoutError,socket.timeout)):return SourceError('TIMEOUT')
 if isinstance(error,ssl.SSLError):return SourceError('TLS')
 if isinstance(error,urllib.error.URLError):
  if isinstance(error.reason,ssl.SSLError):return SourceError('TLS')
  if isinstance(error.reason,(TimeoutError,socket.timeout)):return SourceError('TIMEOUT')
 return SourceError('NETWORK')

def direct_fetch():
 request=urllib.request.Request(PAGE,headers={'User-Agent':'HTKK-Public-Release-Watch/1.0','Accept':'text/html','Accept-Encoding':'identity'})
 try:
  with urllib.request.build_opener(OfficialRedirect()).open(request,timeout=30) as response:
   if response.status!=200:raise SourceError('HTTP_STATUS',response.status)
   if response.headers.get_content_type()!='text/html':raise SourceError('CONTENT_TYPE')
   if response.headers.get('Content-Encoding','identity').lower() not in ('identity',''):raise SourceError('CONTENT_ENCODING')
   data=response.read(MAX_HTML+1);final=official_url(response.url)
 except SourceError:raise
 except Exception as error:raise transport_error(error) from None
 if len(data)>MAX_HTML:raise SourceError('TOO_LARGE')
 return data,final

def relay_fetch(token):
 if not token:raise SourceError('RELAY_AUTH')
 request=urllib.request.Request(RELAY,data=json.dumps({'url':PAGE,'method':'GET','timeoutMs':60000}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','User-Agent':'HTKK-Public-Release-Watch/1.0'},method='POST')
 try:
  with urllib.request.build_opener(NoRedirect()).open(request,timeout=75) as response:raw=response.read(4_000_001)
 except urllib.error.HTTPError as error:raise SourceError('RELAY_AUTH' if error.code in (401,403) else 'RELAY_HTTP',error.code) from None
 except Exception as error:raise transport_error(error) from None
 if len(raw)>4_000_000:raise SourceError('TOO_LARGE')
 try:
  envelope=json.loads(raw)
  if type(envelope.get('status')) is not int or envelope['status']!=200:raise SourceError('RELAY_UPSTREAM',envelope.get('status'))
  if envelope.get('truncated') is not False:raise SourceError('TOO_LARGE')
  headers=envelope.get('headers')
  if not isinstance(headers,dict):raise SourceError('RELAY_ENVELOPE')
  content_type=next((v for k,v in headers.items() if k.lower()=='content-type'),None)
  if not isinstance(content_type,str) or content_type.split(';',1)[0].strip().lower()!='text/html':raise SourceError('CONTENT_TYPE')
  final=official_url(envelope.get('url'));body=envelope.get('body')
  if not isinstance(body,str):raise SourceError('RELAY_ENVELOPE')
  if envelope.get('bodyEncoding')=='text':data=body.encode('utf-8')
  elif envelope.get('bodyEncoding')=='base64':data=base64.b64decode(body,validate=True)
  else:raise SourceError('RELAY_ENVELOPE')
 except SourceError:raise
 except Exception:raise SourceError('RELAY_ENVELOPE') from None
 if len(data)>MAX_HTML:raise SourceError('TOO_LARGE')
 return data,final

def version(text):
 if not isinstance(text,str) or not re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',text):raise SourceError('HTML_PARSE')
 return '.'.join(str(int(part))for part in text.split('.'))

def download_reference(raw):
 # Metadata only: never request this URL. Decode/trim the known trailing-space
 # source href, then accept only a fixed public Fshare file path shape.
 try:
  p=urllib.parse.urlsplit(urllib.parse.urljoin(PAGE,raw.strip()));path=urllib.parse.unquote(p.path).strip(' \t\r\n')
  if p.scheme!='https' or p.hostname not in ('www.fshare.vn','fshare.vn') or p.username or p.password or p.port not in (None,443) or p.query or p.fragment or not re.fullmatch(r'/file/[A-Za-z0-9]{8,32}',path):return {'recognition':'unrecognized','url':None}
  return {'recognition':'recognized-fshare','url':urllib.parse.urlunsplit(('https',p.hostname,path,'',''))}
 except (TypeError,ValueError):return {'recognition':'unrecognized','url':None}

class ReleaseParser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.ignored=0;self.count=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style','noscript'):self.ignored+=1
  if tag=='tr':
   if self.row is not None:raise SourceError('HTML_PARSE')
   self.count+=1
   if self.count>300:raise SourceError('HTML_PARSE')
   self.row={'parts':[],'downloads':[],'textLength':0,'anchors':0}
  if self.row is not None and not self.ignored and tag=='a':
   attrs=dict(attrs)
   if attrs.get('href'):self.row['anchors']+=1
   if 'linkDown' in attrs.get('class','').split():
    href=attrs.get('href','')
    if not isinstance(href,str) or len(href)>2048 or len(self.row['downloads'])>=8:raise SourceError('HTML_PARSE')
    self.row['downloads'].append(download_reference(href))
 def handle_data(self,text):
  if self.row is not None and not self.ignored:
   self.row['textLength']+=len(text)
   if self.row['textLength']>8192:raise SourceError('HTML_PARSE')
   self.row['parts'].append(text)
 def handle_endtag(self,tag):
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
  if tag in ('script','style','noscript') and self.ignored:self.ignored-=1

def release_rows(html):
 if not isinstance(html,str) or len(html.encode('utf-8'))>MAX_HTML:raise SourceError('TOO_LARGE')
 parser=ReleaseParser()
 try:parser.feed(html);parser.close()
 except SourceError:raise
 except Exception:raise SourceError('HTML_PARSE') from None
 if parser.row is not None:raise SourceError('HTML_PARSE')
 result=[]
 for row in parser.rows:
  text=' '.join(' '.join(row['parts']).split());versions=re.findall(r'(?<![\d.])\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])',text);dates=re.findall(r'(?<!\d)\d{2}/\d{2}/\d{4}(?!\d)',text)
  if not row['downloads']:
   if row['anchors'] and versions and dates:raise SourceError('HTML_PARSE')
   continue
  if len(versions)!=1 or len(dates)!=1:raise SourceError('HTML_PARSE')
  try:date=datetime.datetime.strptime(dates[0],'%d/%m/%Y').date()
  except ValueError:raise SourceError('HTML_PARSE') from None
  if not 2000<=date.year<=2100:raise SourceError('HTML_PARSE')
  result.append({'versionAsPublished':versions[0],'version':version(versions[0]),'releaseDateAsPublished':dates[0],'downloadReferences':row['downloads']})
  if len(result)>=12:break
 if not result:raise SourceError('NO_RELEASES')
 return result

def observation(releases):
 published=releases[0]['version'] if releases else None
 references=releases[0]['downloadReferences'] if releases else None
 return {'pinnedVersion':PINNED_VERSION,'firstPublishedVersion':published,'releaseChangedFromPinned':published!=PINNED_VERSION if published else None,'downloadReferenceChangedFromPinned':references!=[{'recognition':'recognized-fshare','url':PINNED_DOWNLOAD}] if references else None,'automaticActivation':False,'compatibilityVerified':False}

def observe(direct=None,relay=None,checked_at=None):
 report={'format':'htkk-public-source-watch-v1','checkedAt':checked_at or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'sourceUrl':PAGE,'scope':'public-release-html-metadata-only','attempts':[],'transport':None,'redirected':False,'finalHost':None,'body':None,'releases':[],'observation':observation([]),'result':'unreachable','failureCode':None}
 for transport,fetch in [('direct-https',direct or direct_fetch),('authorized-relay',relay)]:
  if fetch is None:continue
  try:
   data,final=fetch();official_url(final)
   if not isinstance(data,bytes) or len(data)>MAX_HTML:raise SourceError('TOO_LARGE')
   report['body']={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
   try:html=data.decode('utf-8-sig')
   except UnicodeError:raise SourceError('UTF8') from None
   report['releases']=release_rows(html);report['observation']=observation(report['releases']);report['transport']=transport;report['redirected']=final!=PAGE;report['finalHost']=urllib.parse.urlsplit(final).hostname;report['failureCode']=None
   report['attempts'].append({'transport':transport,'result':'ok','errorCode':None,'httpStatus':200})
   report['result']='review-required' if report['observation']['releaseChangedFromPinned'] or report['observation']['downloadReferenceChangedFromPinned'] else 'unchanged'
   return report
  except Exception as error:
   error=error if isinstance(error,SourceError) else SourceError('INTERNAL')
   report['attempts'].append({'transport':transport,'result':'error','errorCode':error.code,'httpStatus':error.status});report['failureCode']=error.code
   report['result']='invalid' if error.code in ('CONTENT_TYPE','CONTENT_ENCODING','UTF8','HTML_PARSE','NO_RELEASES','TOO_LARGE','RELAY_ENVELOPE') else 'unreachable'
   # No alternate transport may hide TLS/auth or malformed official content.
   if error.code not in ('TIMEOUT','NETWORK','HTTP_DENIED','HTTP_STATUS') or error.status==401 or (error.code=='HTTP_STATUS'and error.status not in (408,429,500,502,503,504)):return report
 return report

def report_path():return pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-official-source-watch.json'
def exact(value,keys):
 if not isinstance(value,dict) or set(value)!=set(keys):raise ValueError('Invalid report schema')
def validate_report(report):
 exact(report,('format','checkedAt','sourceUrl','scope','attempts','transport','redirected','finalHost','body','releases','observation','result','failureCode'))
 if report['format']!='htkk-public-source-watch-v1' or report['sourceUrl']!=PAGE or report['scope']!='public-release-html-metadata-only' or not isinstance(report['checkedAt'],str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00',report['checkedAt']):raise ValueError('Invalid report identity')
 datetime.datetime.fromisoformat(report['checkedAt'])
 if not isinstance(report['attempts'],list) or not 1<=len(report['attempts'])<=2:raise ValueError('Invalid attempts')
 for index,attempt in enumerate(report['attempts']):
  exact(attempt,('transport','result','errorCode','httpStatus'))
  if attempt['transport']!=('direct-https','authorized-relay')[index] or attempt['result'] not in ('ok','error') or attempt['errorCode'] not in ERRORS|{None} or attempt['httpStatus'] is not None and (type(attempt['httpStatus']) is not int or not 100<=attempt['httpStatus']<=599):raise ValueError('Invalid safe attempt')
  if attempt['result']=='ok' and (attempt['errorCode'] is not None or attempt['httpStatus']!=200):raise ValueError('Invalid successful attempt')
  if attempt['result']=='error' and attempt['errorCode'] is None:raise ValueError('Missing safe attempt failure')
 if any(attempt['result']=='ok' for attempt in report['attempts'][:-1]):raise ValueError('Fallback cannot follow success')
 if report['transport'] not in (None,'direct-https','authorized-relay') or type(report['redirected']) is not bool or report['finalHost'] not in HOSTS+(None,) or report['result'] not in ('unchanged','review-required','unreachable','invalid') or report['failureCode'] not in ERRORS|{None}:raise ValueError('Invalid outcome')
 body=report['body']
 if body is not None:
  exact(body,('sha256','bytes'))
  if not isinstance(body['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',body['sha256']) or type(body['bytes']) is not int or not 0<=body['bytes']<=MAX_HTML:raise ValueError('Invalid body metadata')
 if not isinstance(report['releases'],list) or len(report['releases'])>12:raise ValueError('Invalid releases')
 for release in report['releases']:
  exact(release,('versionAsPublished','version','releaseDateAsPublished','downloadReferences'))
  if version(release['versionAsPublished'])!=release['version']:raise ValueError('Invalid release version')
  if not isinstance(release['releaseDateAsPublished'],str) or not re.fullmatch(r'\d{2}/\d{2}/\d{4}',release['releaseDateAsPublished']):raise ValueError('Invalid release date')
  date=datetime.datetime.strptime(release['releaseDateAsPublished'],'%d/%m/%Y').date()
  if not 2000<=date.year<=2100 or not isinstance(release['downloadReferences'],list) or not 1<=len(release['downloadReferences'])<=8:raise ValueError('Invalid release references')
  for reference in release['downloadReferences']:
   exact(reference,('recognition','url'))
   if reference!={'recognition':'unrecognized','url':None} and (reference.get('recognition')!='recognized-fshare' or not isinstance(reference.get('url'),str) or download_reference(reference['url'])!=reference):raise ValueError('Invalid normalized reference')
 expected_observation=observation(report['releases'])
 exact(report['observation'],expected_observation)
 if any(type(report['observation'][key]) is not type(value) or report['observation'][key]!=value for key,value in expected_observation.items()):raise ValueError('Invalid drift result')
 if report['result'] in ('unchanged','review-required'):
  if not report['releases'] or report['transport'] is None or report['body'] is None or report['finalHost'] not in HOSTS or report['failureCode'] is not None or report['attempts'][-1]['result']!='ok' or report['attempts'][-1]['transport']!=report['transport']:raise ValueError('Invalid success report')
  expected='review-required' if report['observation']['releaseChangedFromPinned'] or report['observation']['downloadReferenceChangedFromPinned'] else 'unchanged'
  if expected!=report['result']:raise ValueError('Invalid drift classification')
 elif report['releases'] or report['transport'] is not None or report['finalHost'] is not None or report['redirected'] or report['failureCode'] is None or report['attempts'][-1]['result']!='error' or report['failureCode']!=report['attempts'][-1]['errorCode']:raise ValueError('Invalid failure report')
 if len(json.dumps(report,ensure_ascii=False).encode())>MAX_REPORT:raise ValueError('Report exceeds limit')
 return report

class NoGitRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def api(path,token,payload=None,method=None):
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Private-Source-Observation/1.0'},method=method or ('POST' if payload is not None else 'GET'))
 with urllib.request.build_opener(NoGitRedirect()).open(request,timeout=30) as response:return json.load(response)
def git_sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('Invalid Git SHA')
 return value

def publish(report,token,status_token,run_id,builder_commit,requested_sha=''):
 validate_report(report)
 if not re.fullmatch(r'[0-9]{1,20}',run_id):raise ValueError('Invalid run identifier')
 git_sha(builder_commit)
 if requested_sha:git_sha(requested_sha)
 info=api('',token)
 if info.get('private') is not True or info.get('full_name')!=REPO:raise ValueError('Report target must be fixed private repository')
 source_sha=git_sha(api('/branches/main',token)['commit']['sha'])
 if requested_sha and source_sha!=requested_sha:raise ValueError('Source dispatch superseded')
 private={'format':'htkk-private-source-observation-v1','builderRepository':BUILDER,'builderCommit':builder_commit,'builderRunId':run_id,'sourceSha':source_sha,'report':report}
 body=(json.dumps(private,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
 if len(body)>MAX_REPORT:raise ValueError('Private report exceeds limit')
 blob=git_sha(api('/git/blobs',token,{'content':base64.b64encode(body).decode(),'encoding':'base64'})['sha'])
 tree=git_sha(api('/git/trees',token,{'tree':[{'path':'official-sources.json','mode':'100644','type':'blob','sha':blob}]})['sha'])
 commit=git_sha(api('/git/commits',token,{'message':'Private bounded public HTKK release observation; no automatic activation','tree':tree,'parents':[]})['sha'])
 try:api('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  api('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':commit})
 else:api('/git/refs/heads/'+BRANCH,token,{'sha':commit,'force':True},'PATCH')
 state={'unchanged':'success','review-required':'failure','unreachable':'error','invalid':'error'}[report['result']]
 descriptions={'success':'Nguồn công bố khớp phiên bản đã ghim; chưa xác nhận nghiệp vụ','failure':'Nguồn thay đổi; cần xác minh thủ công trước khi cập nhật','error':'Chưa đọc được metadata nguồn chính thức; không tự kích hoạt'}
 api('/statuses/'+source_sha,status_token,{'state':state,'context':'htkk-source-watch','description':descriptions[state],'target_url':'https://github.com/'+BUILDER+'/actions/runs/'+run_id})
 return commit

def summary(report):return {'result':report['result'],'transport':report['transport'],'pinnedVersion':PINNED_VERSION,'publishedVersion':report['observation']['firstPublishedVersion'],'failureCode':report['failureCode'],'automaticActivation':False}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('observe','publish','outcome'));args=parser.parse_args();path=report_path()
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise ValueError('Unexpected trusted builder')
  if args.mode=='observe':
   fallback=(lambda:relay_fetch(os.environ['AGENT_AUTH_TOKEN'])) if os.environ.get('AGENT_AUTH_TOKEN') else None
   report=validate_report(observe(relay=fallback));path.write_text(json.dumps(report,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary(report),separators=(',',':')))
  else:
   if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_REPORT:raise ValueError('Invalid report file')
   report=validate_report(json.loads(path.read_text(encoding='utf-8')))
   if args.mode=='publish':
    commit=publish(report,os.environ['SOURCE_PUBLISH_TOKEN'],os.environ['SOURCE_STATUS_TOKEN'],os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_SHA'],os.environ.get('REQUESTED_SOURCE_SHA',''));print('Private source observation published: '+commit)
   else:
    print(json.dumps(summary(report),separators=(',',':')))
    return 0 if report['result']=='unchanged' else 1
 except Exception:raise SystemExit('Source watch step failed; no HTML, credentials or raw remote error published.')
 return 0
if __name__=='__main__':raise SystemExit(main())
