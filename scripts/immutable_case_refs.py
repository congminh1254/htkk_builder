"""Private append-only anchors. Only an explicit GET404 permits ref creation."""
import re,urllib.error

def retain(fetch,token,kind,source,case,artifact):
 if kind not in ('input','output')or not re.fullmatch('[a-f0-9]{40}',source)or not re.fullmatch('[a-f0-9]{40}',artifact)or not re.fullmatch('[A-Za-z0-9-]{1,100}',case):raise ValueError('IMMUTABLE_REF')
 name='tags/htkk-case-'+kind+'/'+source+'/'+case+'/'+artifact;ref='refs/'+name
 try:value=fetch('/git/ref/'+name,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  value=fetch('/git/refs',token,{'ref':ref,'sha':artifact})
 if not isinstance(value,dict)or value.get('ref')!=ref or value.get('object',{}).get('type')!='commit'or value['object'].get('sha')!=artifact:raise ValueError('IMMUTABLE_REF')
 return ref
