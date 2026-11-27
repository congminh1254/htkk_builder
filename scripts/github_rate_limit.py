"""Bounded, value-free waits for GitHub API rate-limit responses only.

A response counts as rate limited only when it is HTTP 429, or HTTP 403 carrying a
Retry-After header or X-RateLimit-Remaining: 0. Any other 401/403 is an authorization
failure and is never retried here. GitHub refuses a rate-limited request before acting
on it, so a retry repeats a request that never took effect; callers still retry only
requests whose repetition converges (reads, content-addressed git objects, ref writes
to one exact sha). The response body is never read, and the only text logged is fixed
words and numbers: no URL, header value, body or token.
"""
import email.utils,sys,time,urllib.error

MAX_WAIT=60 # One wait never exceeds this; a longer server-requested wait fails at once.
DEFAULT_WAIT=60 # GitHub: without Retry-After or a reset time, wait at least one minute.
TOTAL=120 # Seconds of rate-limit waiting one process may spend in all.
MAX_RETRIES=3 # Rate-limit retries one process may make in all.

def _header(error,name):
 try:value=(error.headers or {}).get(name)
 except Exception:return None
 return None if value is None else str(value).strip()

def rate_limited(error):
 """True only for 429, or 403 with Retry-After or X-RateLimit-Remaining: 0 (headers only)."""
 if not isinstance(error,urllib.error.HTTPError):return False
 if error.code==429:return True
 return error.code==403 and (_header(error,'Retry-After') is not None or _header(error,'X-RateLimit-Remaining')=='0')

def requested_wait(error,now=None):
 """Seconds the server asked for (Retry-After, else the rate-limit reset time), or None."""
 now=now or time.time
 value=_header(error,'Retry-After')
 if value is not None:
  if value.isdigit():return float(value)
  try:return max(0.0,email.utils.parsedate_to_datetime(value).timestamp()-now())
  except Exception:return None
 reset=_header(error,'X-RateLimit-Reset')
 if _header(error,'X-RateLimit-Remaining')=='0' and reset is not None and reset.isdigit():return max(0.0,float(reset)-now())+1
 return None

def _log(text):print(text,file=sys.stderr,flush=True)

class Budget:
 """The rate-limit waits of one process: at most MAX_RETRIES waits, each <= max_wait, <= total in all."""
 def __init__(self,total=TOTAL,max_wait=MAX_WAIT,retries=MAX_RETRIES,sleep=None,now=None,log=None):
  self.total=total;self.max_wait=max_wait;self.max_retries=retries
  # Late-bound so a patched time.sleep/time.time applies.
  self.sleep=sleep or (lambda seconds:time.sleep(seconds));self.now=now or (lambda:time.time());self.log=log or _log
  self.spent=0.0;self.retries=0
 def wait(self,error):
  """Sleep as the server asked and return True, or return False when the error must be raised."""
  if not rate_limited(error):return False
  requested=requested_wait(error,self.now)
  delay=float(DEFAULT_WAIT if requested is None else requested)
  if delay>self.max_wait or self.retries>=self.max_retries or self.spent+delay>self.total:
   self.log('GitHub API rate limit (HTTP '+str(error.code)+'); the wait does not fit the bounded retry budget, not retried.')
   return False
  self.retries+=1;self.spent+=delay
  self.log('GitHub API rate limit (HTTP '+str(error.code)+'); waiting '+str(int(-(-delay//1)))+' s, bounded retry '+str(self.retries)+' of '+str(self.max_retries)+'.')
  self.sleep(delay)
  return True

_PROCESS=None
def process_budget():
 """The single budget shared by every transport call in this process."""
 global _PROCESS
 if _PROCESS is None:_PROCESS=Budget()
 return _PROCESS
