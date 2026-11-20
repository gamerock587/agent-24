import asyncio
import ipaddress
import socket
import time
from urllib.parse import urlsplit,urlunsplit,urljoin
import httpx

class ScopeError(ValueError):pass

def normalize(url):
    if '://' not in url:url='https://'+url
    p=urlsplit(url.strip())
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:raise ScopeError('Use an HTTP(S) URL without credentials.')
    host=p.hostname.encode('idna').decode().lower().rstrip('.')
    if len(url)>2000 or any(c in url for c in ('\\','\r','\n','\x00')):raise ScopeError('Invalid URL')
    try:port=p.port
    except ValueError:raise ScopeError('Invalid port')
    netloc=('['+host+']' if ':' in host else host)+((':'+str(port)) if port and port!={'http':80,'https':443}[p.scheme] else '')
    return urlunsplit((p.scheme,netloc,p.path or '/',p.query,''))

def origin(url):
    p=urlsplit(normalize(url));return p.scheme+'://'+p.netloc

def in_scope(run,url):
    """The submitted hostname is the boundary; never infer its parent domain."""
    try:
        value=normalize(url);target=normalize(run.get('_seed_url',run['url']))
        if origin(value)==origin(target):return True
        p=urlsplit(value);seed=urlsplit(target)
        try:ipaddress.ip_address(seed.hostname);return False
        except ValueError:pass
        if seed.hostname=='localhost':return False
        if not run['spec'].get('include_subdomains'):return False
        if p.port not in (None,80,443) or seed.port not in (None,80,443):return False
        return p.hostname==seed.hostname or p.hostname.endswith('.'+seed.hostname)
    except ValueError:return False

async def resolve(url,allowed_local=()):
    url=normalize(url);p=urlsplit(url)
    values=await asyncio.to_thread(socket.getaddrinfo,p.hostname,p.port or (443 if p.scheme=='https' else 80),0,socket.SOCK_STREAM)
    all_ips=sorted({v[4][0] for v in values})
    if not all_ips:raise ScopeError('DNS returned no addresses')
    local=origin(url) in allowed_local
    if not local and any(not ipaddress.ip_address(ip).is_global for ip in all_ips):raise ScopeError('Target resolves to a private/reserved address; only configured local labs are allowed.')
    if local and any(not ipaddress.ip_address(ip).is_loopback for ip in all_ips):raise ScopeError('Configured local labs must remain loopback-only.')
    # Prefer IPv4 when available; some environments cannot route IPv6 directly.
    ipv4=[v[4][0] for v in values if v[0]==socket.AF_INET]
    return (sorted(set(ipv4)) or all_ips)[0]

class Network:
    def __init__(self,settings):self.s=settings;self.locks={};self.last={}
    async def fetch(self,run,url,headers=None,method='GET'):
        url=normalize(url)
        if not in_scope(run,url):raise ScopeError('The proposed request leaves the configured target scope.')
        if method not in ('GET','HEAD','OPTIONS'):raise ScopeError('This release only executes bounded read-only HTTP methods.')
        host=urlsplit(url).hostname;lock=self.locks.setdefault(host,asyncio.Lock())
        redirects=[]
        async with lock:
            for _ in range(4):
                if run['requests']>=run['spec']['max_requests']:raise ScopeError('Request budget reached.')
                await asyncio.sleep(max(0,self.s['request_interval']-(time.monotonic()-self.last.get(host,0))))
                ip=await resolve(url,self.s['local_lab_origins']);p=urlsplit(url)
                request_headers={'User-Agent':'Agent24/0.1 authorized-lab-assessment','Host':p.netloc,'Accept':'text/html,application/json,text/plain;q=0.8',**(headers or {})}
                async with httpx.AsyncClient(timeout=self.s['request_timeout'],trust_env=False,follow_redirects=False) as client:
                    req=client.build_request(method,url,headers=request_headers)
                    # IPv6 addresses must be bracketed in URLs: [addr] not addr.
                    url_host='['+ip+']' if ':' in ip else ip
                    req.url=req.url.copy_with(host=url_host);req.extensions['sni_hostname']=p.hostname
                    # DNS awaits can overlap on different hosts. Recheck immediately
                    # before the synchronous reservation to keep a shared run budget.
                    if run['requests']>=run['spec']['max_requests']:raise ScopeError('Request budget reached.')
                    started=time.monotonic();run['requests']+=1;self.last[host]=time.monotonic()
                    r=await client.send(req,stream=True)
                    try:
                        raw=bytearray();truncated=False
                        byte_limit=self.s.get('javascript_byte_limit',1048576) if p.path.endswith(('.js','.map')) else 262144
                        async for chunk in r.aiter_bytes():
                            raw.extend(chunk)
                            if len(raw)>byte_limit:raw=raw[:byte_limit];truncated=True;break
                        result={'url':url,'method':method,'status':r.status_code,'headers':dict(r.headers),'body':bytes(raw).decode('utf8',errors='replace'),'bytes':len(raw),'truncated':truncated,'duration_ms':round((time.monotonic()-started)*1000,1),'resolved_ip':ip,'redirect_chain':list(redirects)}
                    finally:await r.aclose()
                if r.status_code in (301,302,303,307,308) and r.headers.get('location'):
                    next_url=normalize(urljoin(url,r.headers['location']))
                    redirects.append({'url':url,'status':r.status_code,'location':next_url});result['redirect_chain']=list(redirects)
                    if origin(next_url)!=origin(url):
                        result['redirect_discovered' if in_scope(run,next_url) else 'redirect_blocked']=next_url;return result
                    url=next_url;continue
                return result
        raise ScopeError('Redirect limit reached.')

