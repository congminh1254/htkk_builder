"""Offline git object model for API fakes (tests only).

An independent implementation of git blob/tree ids: a fake tree request answers the id git would give the
files it describes (inline content or earlier blobs, over an optional base tree), so a publisher's local
tree-id verification is checked against a second implementation, not against itself.
"""
import base64,hashlib,io,tarfile

def blob_id(body):return hashlib.sha1(b'blob %d\0'%len(body)+body).hexdigest()

def tree_id(files):
 """Id of the git tree of {path: bytes} (nested by '/')."""
 directories={};blobs={}
 for path,body in files.items():
  if '/' in path:
   head,rest=path.split('/',1);directories.setdefault(head,{})[rest]=body
  else:blobs[path]=body
 rows=[(name,b'100644',bytes.fromhex(blob_id(body))) for name,body in blobs.items()]
 rows+=[(name+'/',b'40000',bytes.fromhex(tree_id(children))) for name,children in directories.items()]
 content=b''.join(mode+b' '+name.rstrip('/').encode()+b'\0'+raw for name,mode,raw in sorted(rows,key=lambda row:row[0].encode()))
 return hashlib.sha1(b'tree %d\0'%len(content)+content).hexdigest()

class Git:
 """Remembers blobs and trees written through a fake API."""
 def __init__(self):self.blobs={};self.trees={}
 def blob(self,payload):
  body=base64.b64decode(payload['content']);value=blob_id(body);self.blobs[value]=body;return {'sha':value}
 def tree(self,payload,store_inline=lambda body:body):
  files=dict(self.trees[payload['base_tree']]) if 'base_tree' in payload else {}
  for entry in payload['tree']:
   files[entry['path']]=store_inline(entry['content'].encode('utf-8')) if 'content' in entry else self.blobs[entry['sha']]
  value=tree_id(files);self.trees[value]=files
  return {'sha':value,'tree':[{'path':name,'sha':'0'*40} for name in sorted({path.split('/',1)[0] for path in files})],'truncated':False}

def written(payloads):
 """Bytes of every file a list of tree payloads wrote, in request order (inline content only)."""
 return [entry['content'].encode('utf-8') for payload in payloads for entry in payload['tree'] if 'content' in entry]

def tree_payloads(calls):
 """Payloads of the tree requests in recorded calls of any shape (path first, payload next)."""
 return [call[1] if isinstance(call[1],dict) else call[2] for call in calls if call[0]=='/git/trees']

def tarball(commit,files,prefix=None,extra=()):
 """A gzip tar laid out as GitHub's commit archive: a pax global header naming the commit, one root directory."""
 prefix=prefix or 'htkk-net-htkk_web-'+commit[:7];buffer=io.BytesIO()
 with tarfile.open(fileobj=buffer,mode='w:gz',format=tarfile.PAX_FORMAT,pax_headers={'comment':commit}) as archive:
  def add(name,body=None,kind=tarfile.REGTYPE,mode=0o664):
   info=tarfile.TarInfo(name);info.type=kind;info.mode=mode
   if body is None:archive.addfile(info)
   else:info.size=len(body);archive.addfile(info,io.BytesIO(body))
  add(prefix+'/',kind=tarfile.DIRTYPE,mode=0o775)
  for directory in sorted({path.rsplit('/',1)[0] for path in files if '/' in path}):add(prefix+'/'+directory+'/',kind=tarfile.DIRTYPE,mode=0o775)
  for path,body in sorted(files.items()):add(prefix+'/'+path,body)
  for item in extra:add(*item)
 return buffer.getvalue()
