"""Bounded, value-free retries for the idempotent native-case status callback.

Only transient GitHub API classes are retried: HTTP 5xx, 429, 403 carrying
secondary/primary rate-limit semantics, and connection resets/timeouts.
Authentication, permission, not-found and validation errors (401/403/404/422)
fail at once. Nothing printed here contains a URL, a header or a response body.
"""
import email.utils,http.client,random,socket,time,urllib.error
BACKOFF=(2,4,8,16,32,64) # Exponential base delays; jitter adds up to 50%.
TOTAL=180 # Wall-clock seconds one callback may spend before giving up.
MAX_RETRY_AFTER=90 # A longer server-requested wait is not honored; fail instead.
class Exhausted(Exception):pass
class Budget:
 def __init__(self,total=TOTAL,sleep=time.sleep,rand=random.random,clock=time.monotonic,log=print):
  self.total=total;self.sleep=sleep;self.rand=rand;self.clock=clock;self.log=log;self.start=clock();self.retries=0
 def remaining(self):return self.total-(self.clock()-self.start)
def _header(error,name):
 try:return (error.headers or {}).get(name)
 except Exception:return None
def _rate_limited_403(error):
 if _header(error,'Retry-After')is not None or _header(error,'X-RateLimit-Remaining')=='0':return True
 try:body=error.read(8192)or b''
 except Exception:return False
 # Inspected in memory only; never printed or re-raised with the body.
 return b'rate limit' in body.lower() or b'abuse' in body.lower()
def classify(error):
 """A value-free label for a transient error, or None when it must not be retried."""
 if isinstance(error,urllib.error.HTTPError):
  if 500<=error.code<=599:return 'HTTP '+str(error.code)
  if error.code==429:return 'HTTP 429'
  if error.code==403 and _rate_limited_403(error):return 'HTTP 403 rate limit'
  return None
 if isinstance(error,(TimeoutError,socket.timeout)):return 'timeout'
 if isinstance(error,(ConnectionError,http.client.RemoteDisconnected,http.client.IncompleteRead)):return 'connection'
 if isinstance(error,urllib.error.URLError):return 'connection' if not isinstance(error.reason,str) or 'certificate' not in error.reason.lower() else None
 if isinstance(error,http.client.HTTPException):return 'connection'
 return None
def server_wait(error,now=time.time):
 """Seconds the server asked us to wait (Retry-After or rate-limit reset), if any."""
 if not isinstance(error,urllib.error.HTTPError):return None
 value=_header(error,'Retry-After')
 if value is not None:
  value=str(value).strip()
  if value.isdigit():return float(value)
  try:return max(0.0,email.utils.parsedate_to_datetime(value).timestamp()-now())
  except Exception:return None
 reset=_header(error,'X-RateLimit-Reset')
 if _header(error,'X-RateLimit-Remaining')=='0' and reset is not None and str(reset).strip().isdigit():return max(0.0,float(reset)-now())+1
 return None
def call(fn,budget,label='request'):
 """Run fn(), retrying transient failures with jittered exponential backoff within budget."""
 for attempt in range(len(BACKOFF)+1):
  try:return fn()
  except Exception as error:
   kind=classify(error)
   if kind is None or attempt==len(BACKOFF):raise
   requested=server_wait(error)
   if requested is not None and requested>MAX_RETRY_AFTER:raise
   delay=BACKOFF[attempt]*(1+0.5*budget.rand())
   if requested is not None:delay=max(delay,requested)
   if delay>budget.remaining():raise Exhausted(label) from None
   budget.retries+=1
   budget.log('Transient native callback API error ('+kind+') on '+label+'; bounded retry '+str(attempt+1)+' of '+str(len(BACKOFF))+'.',flush=True)
   budget.sleep(delay)
