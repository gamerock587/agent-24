"""Bounded discovery from observed documents and passive certificate names.

This module proposes URLs. Only Network can execute target requests, and it
independently enforces hostname, DNS, method, rate and request budgets.
"""
import asyncio
import html
import ipaddress
import json
import re
import shutil
import uuid
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,urlunsplit,parse_qsl,urlencode
import httpx
from .network import normalize,in_scope,resolve

UNSAFE=re.compile(r'(?:logout|logoff|signout|delete|remove|purchase|checkout|reset|cancel|add.?to.?cart|unsubscribe|terminate|drop|destroy|transfer|payment)',re.I)
ASSET=re.compile(r'\.(?:png|jpe?g|gif|webp|svg|ico|woff2?|ttf|mp[34]|avi|zip|gz|pdf|exe|dmg|css)(?:$)',re.I)

def identity(url):
    p=urlsplit(normalize(url))
    return urlunsplit((p.scheme,p.netloc,p.path,urlencode(sorted(parse_qsl(p.query,keep_blank_values=True))),''))

def fetchable(url):
    p=urlsplit(url)
    return not UNSAFE.search(p.path+' '+p.query) and not ASSET.search(p.path)

class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.urls=[];self.forms=[];self.form=None;self.inline=[];self.in_script=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('a','iframe') and a.get('href' if tag=='a' else 'src'):
            self.urls.append((a.get('href' if tag=='a' else 'src'),'html-link'))
        if tag=='script':
            self.in_script=True
            if a.get('src'):self.urls.append((a['src'],'javascript-bundle'))
        if tag=='form':
            self.form={'action':a.get('action',''),'method':a.get('method','GET').upper(),'inputs':[]};self.forms.append(self.form)
        if self.form is not None and tag in ('input','textarea','select') and a.get('name'):
            self.form['inputs'].append({'name':a['name'],'value':a.get('value',''),'type':a.get('type','text')})
    def handle_endtag(self,tag):
        if tag=='form':self.form=None
        if tag=='script':self.in_script=False
    def handle_data(self,data):
        if self.in_script:self.inline.append(data)

def js_routes(body):
    # Static strings are leads, never evaluated as JavaScript or model instructions.
    output=[]
    for m in re.finditer(r'''["'`]((?:https?://|/|\./|\.\./)[^"'`\s<>]{1,500})["'`]''',body):
        value=m.group(1)
        if '${' in value or any(c in value for c in ('*','<','>','\\')):continue
        path=urlsplit(value).path
        if path in ('/$','/&','/a','/a/b','/a/i','/_next/','/_next/st','/_next/image') or path.endswith(('/chunks/app/','/static/media/')):continue
        if not re.search(r'[A-Za-z0-9]',path) and not value.startswith(('http://','https://')):continue
        output.append((value,'javascript-route'))
    for m in re.finditer(r'[#@]\s*sourceMappingURL=([^\s*]+)',body):
        if not m[1].startswith('data:'):output.append((m[1],'source-map-reference'))
    return output

def extract(response):
    url=response['url'];body=response['body'];kind=response['headers'].get('content-type','').lower()
    leads=[];forms=[]
    if 'html' in kind or re.search(r'<(?:html|a|form|script)\b',body[:4000],re.I):
        parser=Document();parser.feed(body);leads.extend(parser.urls);forms=parser.forms
        for script in parser.inline:leads.extend(js_routes(script))
        for form in forms:
            # Only observed GET forms without password/file/action fields.
            if form['method']=='GET' and not any(x['type'] in ('password','file') or UNSAFE.search(x['name']) for x in form['inputs']):
                try:action=normalize(urljoin(url,html.unescape(form['action'])))
                except ValueError:continue
                p=urlsplit(action);pairs=parse_qsl(p.query,keep_blank_values=True)
                pairs.extend((x['name'],x['value'] or 'agent24') for x in form['inputs'][:8] if x['type'] not in ('checkbox','radio','submit'))
                leads.append((urlunsplit((p.scheme,p.netloc,p.path,urlencode(pairs),'')),'get-form'))
    if 'javascript' in kind or urlsplit(url).path.endswith('.js'):leads.extend(js_routes(body))
    if urlsplit(url).path.endswith('/robots.txt'):
        for line in body.splitlines():
            match=re.match(r'\s*(?:Allow|Disallow|Sitemap)\s*:\s*(\S+)',line,re.I)
            if match and '*' not in match[1] and '$' not in match[1]:leads.append((match[1],'robots-policy'))
    if 'xml' in kind or urlsplit(url).path.endswith('.xml'):
        if '<!DOCTYPE' not in body.upper() and '<!ENTITY' not in body.upper():
            try:
                tree=ET.fromstring(body)
                for item in tree.iter():
                    if item.tag.split('}')[-1]=='loc' and item.text:leads.append((item.text.strip(),'sitemap'))
            except ET.ParseError:pass
    # Public OpenAPI descriptions: record GET routes; never submit mutations.
    if 'json' in kind:
        try:
            payload=json.loads(body)
            if isinstance(payload,dict) and isinstance(payload.get('paths'),dict) and ('openapi' in payload or 'swagger' in payload):
                for path,methods in payload['paths'].items():
                    if isinstance(methods,dict) and 'get' in methods and '{' not in path:leads.append((path,'openapi-get-route'))
        except (ValueError,TypeError):pass
    output=[];seen=set()
    for href,source in leads[:500]:
        try:value=identity(urljoin(url,html.unescape(href)))
        except ValueError:continue
        if value not in seen:seen.add(value);output.append({'url':value,'source':source,'parent':url})
    return {'urls':output,'forms':forms[:40]}

async def passive_names(host):
    """Prefer installed Subfinder; otherwise query certificate transparency only."""
    binary=shutil.which('subfinder')
    if binary:
        proc=await asyncio.create_subprocess_exec(binary,'-d',host,'-silent','-timeout','15','-max-time','1',stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        try:
            out,err=await asyncio.wait_for(proc.communicate(),35)
            if proc.returncode:raise RuntimeError('Subfinder failed: '+err.decode(errors='replace')[:200])
            return out.decode(errors='replace').splitlines()[:2000],'installed-subfinder'
        finally:
            if proc.returncode is None:proc.kill();await proc.wait()
    async with httpx.AsyncClient(timeout=20,trust_env=False,follow_redirects=False) as client:
        async with client.stream('GET','https://crt.sh/',params={'q':'%.'+host,'output':'json'}) as response:
            response.raise_for_status();raw=bytearray()
            async for chunk in response.aiter_bytes():
                raw.extend(chunk)
                if len(raw)>2_000_000:raise ValueError('Certificate source response exceeded 2 MB budget')
    rows=json.loads(raw)
    if not isinstance(rows,list):raise ValueError('Certificate source returned an unexpected document')
    return [name for row in rows[:5000] if isinstance(row,dict) for name in str(row.get('name_value','')).splitlines()][:2000],'certificate-transparency'

async def discover(run,baseline,settings):
    seed=urlsplit(run.get('_seed_url',run['url']));host=seed.hostname
    try:ipaddress.ip_address(host);local=True
    except ValueError:local=host=='localhost'
    if local or not run['spec'].get('include_subdomains'):
        return {'status':'completed','hosts':[],'sources':[],'errors':[],'note':'Subdomain discovery disabled for this scope.','findings':[]}
    names={host:{'source':'submitted-host'}};errors=[];sources=[]
    for lead in extract(baseline)['urls']:
        if in_scope(run,lead['url']):names.setdefault(urlsplit(lead['url']).hostname,{'source':'observed-document'})
    try:
        found,source=await passive_names(host);sources.append(source)
        for name in found:
            name=name.lower().strip().lstrip('*.').rstrip('.')
            if re.fullmatch(r'[a-z0-9.-]+',name) and (name==host or name.endswith('.'+host)):names.setdefault(name,{'source':source})
    except Exception as exc:errors.append({'source':'passive-discovery','error':type(exc).__name__+': '+str(exc)[:200]})
    guesses=['www','api','app','admin','auth','login','dev','staging','test','portal','cdn','static']
    for prefix in guesses:names.setdefault(prefix+'.'+host,{'source':'bounded-dns-candidate'})
    semaphore=asyncio.Semaphore(6);wildcard=None
    try:wildcard=await asyncio.wait_for(resolve('https://agent24-'+uuid.uuid4().hex[:12]+'.'+host,settings['local_lab_origins']),4)
    except (OSError,ValueError,TimeoutError):pass
    async def check(name,meta):
        async with semaphore:
            # Resolve only; reachability requires a separate, budgeted HTTP action.
            candidate=f'{seed.scheme}://{name}/'
            try:
                ip=await asyncio.wait_for(resolve(candidate,settings['local_lab_origins']),4)
                wildcard_guess=meta['source']=='bounded-dns-candidate' and ip==wildcard
                return {'host':name,**meta,'resolved_ip':ip,'url':candidate,'status':'wildcard-unverified' if wildcard_guess else 'resolved'}
            except Exception as exc:return {'host':name,**meta,'url':candidate,'status':'unresolved','reason':type(exc).__name__+': '+str(exc)[:160]}
    limit=run['spec'].get('max_dns_queries',64)
    checked=await asyncio.gather(*(check(name,meta) for name,meta in list(names.items())[:limit]))
    return {'status':'partial' if errors or len(names)>limit else 'completed','hosts':checked,'sources':sources+['observed-document','bounded-dns-candidates'],'errors':errors,'wildcard_ip':wildcard,'remaining_dns_candidates':max(0,len(names)-limit),'findings':[],'note':'Certificate names and DNS resolution are discovery evidence, not proof of an active application or a vulnerability.'}
