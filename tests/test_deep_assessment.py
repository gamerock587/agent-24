import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
import pytest
from app.config import SETTINGS
from app.engine import Engine
from app.network import Network,ScopeError,in_scope
from app.recon import extract,discover
from app.store import Store
from app.api import RunSpec

class Models:
    calls=[]
    async def generate(self,*args,**kwargs):
        if args[0].startswith('Select evidence-based'):return {'priorities':['remaining-coverage']}
        return 'Prioritize the observed parameter differentials, JSON API surface and response exposure signatures.'
    async def choose(self,state,actions):return actions[0],{'choice':'0'}

def spec(**changes):
    return RunSpec(url='https://example.test/').model_dump(exclude={'url'})|{'max_seconds':60,'force_retest':False,**changes}

def response(url,body,kind='text/html',status=200):
    return {'url':url,'body':body,'status':status,'headers':{'content-type':kind},'bytes':len(body),'resolved_ip':'93.184.215.14'}

def test_descendant_scope_never_widens_to_parent_or_suffix_matches():
    r={'url':'https://tenant.example.com/','spec':spec()}
    assert in_scope(r,'https://api.tenant.example.com/data')
    assert in_scope(r,'http://tenant.example.com/')
    for url in ('https://example.com/','https://sibling.example.com/','https://tenant.example.com.attacker.test/','https://api.tenant.example.com:9999/'):
        assert not in_scope(r,url)
    assert not in_scope({'url':'http://127.0.0.1:7777/','spec':spec()},'http://127.0.0.1:8888/')
    assert not in_scope({'url':r['url'],'spec':spec(include_subdomains=False)},'https://api.tenant.example.com/')

def test_document_route_sources_and_get_form_inputs():
    r=response('https://example.test/a/',"""<form action='/search' method='get'><input name='q' value='first'><input name='page' value='2'><input type='submit' name='go'></form><form method='post' action='/upload'><input type='file' name='file'></form><script src='/app.js'></script><script>fetch('/api/items')</script><a href='https://outside.test/'>outside</a>""")
    found=extract(r);urls={x['url'] for x in found['urls']}
    assert 'https://example.test/search?page=2&q=first' in urls
    assert 'https://example.test/app.js' in urls and 'https://example.test/api/items' in urls
    assert not any('/upload' in u for u in urls)
    assert len(found['forms'])==2
    assert extract(response('https://example.test/robots.txt','Disallow: /hidden\nSitemap: /map.xml','text/plain'))['urls'][0]['source']=='robots-policy'
    assert extract(response('https://example.test/map.xml','<urlset><url><loc>https://example.test/nested</loc></url></urlset>','application/xml'))['urls'][0]['source']=='sitemap'
    assert extract(response('https://example.test/openapi.json',json.dumps({'openapi':'3.0.0','paths':{'/api/get':{'get':{}},'/api/post':{'post':{}}}}),'application/json'))['urls'][0]['url']=='https://example.test/api/get'

@pytest.mark.asyncio
async def test_subdomain_names_wildcard_and_source_failure_are_visible(monkeypatch):
    async def passive(host):return ['api.example.test','*.example.test','outside.test','private.example.test'],'fixture-passive'
    async def dns(url,allowed=()):
        host=urlsplit(url).hostname
        if host=='private.example.test':raise ScopeError('Private address rejected')
        if host=='api.example.test':return '8.8.4.4'
        return '8.8.8.8' # wildcard candidates cannot be treated as live hosts
    monkeypatch.setattr('app.recon.passive_names',passive);monkeypatch.setattr('app.recon.resolve',dns)
    r={'url':'https://example.test/','spec':spec(max_dns_queries=32)}
    result=await discover(r,response(r['url'],'<a href="https://app.example.test/">app</a>'),SETTINGS)
    assert not any(h['host']=='outside.test' for h in result['hosts'])
    assert next(h for h in result['hosts'] if h['host']=='api.example.test')['status']=='resolved'
    assert next(h for h in result['hosts'] if h['host']=='www.example.test')['status']=='wildcard-unverified'
    assert next(h for h in result['hosts'] if h['host']=='private.example.test')['status']=='unresolved'
    async def failure(host):raise TimeoutError('fixture source timeout')
    monkeypatch.setattr('app.recon.passive_names',failure)
    assert (await discover(r,response(r['url'],''),SETTINGS))['errors'][0]['source']=='passive-discovery'

@pytest.fixture
def site():
    state={'change':False,'seen':[]}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state['seen'].append(self.path);p=urlsplit(self.path);status=200;kind='text/html'
            pages={
                '/':"<a href='/level1'>level one</a><script src='/app.js'></script><a href='/logout'>logout</a><a href='https://outside.invalid/'>outside</a>",
                '/level1':"<a href='/level2'>level two</a>",
                '/level2':"<form action='/search' method='get'><input name='q' value='seed'><input name='page' value='1'></form><form action='/upload' method='post'><input type='file' name='file'></form>",
                '/robots.txt':'Disallow: /hidden\nSitemap: /map.xml',
                '/sitemap.xml':'<sitemapindex><sitemap><loc>/map.xml</loc></sitemap></sitemapindex>',
                '/map.xml':'<urlset><url><loc>/indexed</loc></url></urlset>',
                '/hidden':'<title>Index of /hidden</title>',
                '/indexed':"<a href='/guarded'>guarded</a>",
                '/app.js':"fetch('/api/schema');fetch('/api/items')",
                '/.well-known/security.txt':'Contact: mailto:security@example.test',
            }
            body=pages.get(p.path,'not found')
            if p.path=='/guarded':status=403;body='Login required'
            elif p.path=='/api/schema':kind='application/json';body=json.dumps({'openapi':'3.0.0','paths':{'/api/detail':{'get':{}},'/api/mutate':{'post':{}}}})
            elif p.path in ('/api/items','/api/detail'):kind='application/json';body='{"items": []}'
            elif p.path=='/search':
                q=parse_qs(p.query);body='SQL syntax MySQL error' if any("'" in v for values in q.values() for v in values) else 'Search: '+str(q)+(' changed' if state['change'] else '')
            elif p.path not in pages and p.path!='/guarded':status=404
            self.send_response(status);self.send_header('Content-Type',kind);self.end_headers();self.wfile.write(body.encode())
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    yield f'http://127.0.0.1:{server.server_port}/',state
    server.shutdown();server.server_close()

@pytest.mark.asyncio
async def test_recursive_crawl_tests_each_parameter_memory_and_barriers(tmp_path,site):
    url,state=site;cfg={**SETTINGS,'request_interval':0,'request_timeout':2,'local_lab_origins':[url.rstrip('/')]}
    db=Store(tmp_path/'deep.sqlite3');e=Engine(db,cfg,Models());e.slots=3
    settings=spec(include_subdomains=False,max_pages=40,crawl_depth=6,max_requests=100,max_actions=150)
    async def assess():
        run=db.create(url,'127.0.0.1',settings);await e.assess(run['id'],'fixture');return db.detail(run['id'])
    first=await assess();coverage=first['coverage'];paths={urlsplit(p['url']).path for p in coverage['endpoints'] if p['status'] in ('fetched','access-barrier')}
    assert {'/level2','/search','/hidden','/indexed','/api/items','/api/detail','/guarded'}<=paths
    assert not any(p.startswith('/logout') or p.startswith('/upload') or p.startswith('/api/mutate') for p in state['seen'])
    probes=[a for a in first['actions'] if a['tool']=='database_error_probe'];assert len(probes)==2
    assert all(a['result']['findings'] for a in probes)
    assert any(f['endpoint'].endswith('/hidden') for f in first['findings'])
    assert all(f['status']=='candidate' for f in first['findings'])
    assert coverage['stop_reason']=='access-or-availability-barriers' and first['status']=='partial'
    assert any(s['reason']=='outside-scope' for s in coverage['skipped'])
    assert any(a['tool']=='api_inventory' for a in first['actions'])
    second=await assess();assert second['requests']<first['requests'];assert all(a['status']=='reused' for a in second['actions'] if a['tool']=='database_error_probe')
    state['change']=True
    third=await assess();assert all(a['status']=='completed' for a in third['actions'] if a['tool']=='database_error_probe')
    assert all(a['status']=='reused' for a in third['actions'] if a['tool']=='content_review' and a['url'].endswith('/hidden'))
    db.db.close()

@pytest.mark.asyncio
async def test_budget_exhaustion_leaves_truthful_unfinished_frontier(tmp_path,site):
    url,state=site;cfg={**SETTINGS,'request_interval':0,'request_timeout':2,'local_lab_origins':[url.rstrip('/')]}
    db=Store(tmp_path/'budget.sqlite3');e=Engine(db,cfg,Models());e.slots=3
    run=db.create(url,'127.0.0.1',spec(include_subdomains=False,max_requests=3,max_actions=20,max_pages=40,crawl_depth=5))
    await e.assess(run['id'],'budget');d=db.detail(run['id'])
    assert d['requests']<=3 and d['status']=='partial'
    assert d['coverage']['frontier_remaining']>0 and d['coverage']['stop_reason']
    assert any(a['tool']=='content_review' for a in d['actions']) # Offline checks remain possible after crawl limits.
    db.db.close()

@pytest.mark.asyncio
async def test_resolved_subdomain_gets_a_separate_application_assessment(tmp_path,monkeypatch):
    async def discovery(run,baseline,settings):
        return {'status':'completed','hosts':[{'host':'api.example.test','status':'resolved','url':'https://api.example.test/','source':'fixture'}],'errors':[],'findings':[]}
    monkeypatch.setattr('app.recon.discover',discovery)
    class NetworkFixture:
        async def fetch(self,run,url,headers=None,method='GET'):
            assert in_scope(run,url);run['requests']+=1
            if url=='https://api.example.test/':return response(url,'{"items":[]}','application/json')
            return response(url,'<html></html>' if url=='https://example.test/' else 'not found',status=200 if url.endswith('.test/') else 404)
    db=Store(tmp_path/'hosts.sqlite3');e=Engine(db,SETTINGS,Models(),NetworkFixture());e.slots=3
    r=db.create('https://example.test/','example.test',spec());await e.assess(r['id'],'hosts');d=db.detail(r['id'])
    assert d['coverage']['hosts']==['api.example.test','example.test']
    assert any(a['tool']=='api_inventory' and 'api.example.test' in a['url'] for a in d['actions'])
    assert d['status']=='completed';db.db.close()

@pytest.mark.asyncio
async def test_saved_evidence_review_keeps_history_and_fresh_probe_controls(tmp_path,site):
    url,state=site;cfg={**SETTINGS,'request_interval':0,'request_timeout':2,'local_lab_origins':[url.rstrip('/')]}
    db=Store(tmp_path/'review.sqlite3');e=Engine(db,cfg,Models());e.slots=3
    settings=spec(include_subdomains=False,file_checks=False,analyze_evidence=False,max_pages=40,crawl_depth=6,max_requests=100,max_actions=150)
    first=db.create(url,'127.0.0.1',settings);await e.assess(first['id'],'first')
    state['seen'].clear()
    second=db.create(url,'127.0.0.1',{**settings,'review_from':first['id'],'force_retest':True})
    await e.assess(second['id'],'review');d=db.detail(second['id'])
    assert d['coverage']['historical_responses']>=10 and d['coverage']['fresh_responses']==1
    assert not any(p=='/level1' or p=='/level2' for p in state['seen'])
    assert len([p for p in state['seen'] if p.startswith('/search')])>=8
    assert any(a['name']=='historical-response.json' for a in d['artifacts'])
    third=db.create(url,'127.0.0.1',{**settings,'review_from':second['id']})
    await e.assess(third['id'],'review-again')
    assert db.detail(third['id'])['coverage']['historical_responses']>=10
    db.db.close()

@pytest.mark.asyncio
async def test_javascript_results_trigger_real_backend_verification(tmp_path):
    class Net:
        async def fetch(self,run,url,headers=None,method='GET'):
            assert in_scope(run,url);run['requests']+=1
            if url=='https://example.test/':return response(url,'<script src="/app.js"></script>')
            if url=='https://example.test/app.js':return response(url,'const client=axios.create({baseURL:"https://api.example.test"});client.get("/items");headers.get("content-type");','application/javascript')
            if url=='https://api.example.test/items':return response(url,'{"error":"authentication required"}','application/json',401)
            return response(url,'missing',status=404)
    db=Store(tmp_path/'mapped.sqlite3');e=Engine(db,SETTINGS,Models(),Net());e.slots=3
    # Avoid passive discovery; scope still includes the client-named descendant.
    from unittest.mock import patch
    async def discovery(*args):return {'status':'completed','hosts':[],'errors':[],'findings':[]}
    with patch('app.recon.discover',discovery):
        r=db.create('https://example.test/','example.test',spec(file_checks=False,analyze_evidence=False));await e.assess(r['id'],'mapped')
    detail=db.detail(r['id']);probes=[a for a in detail['actions'] if a['tool']=='api_route_probe']
    assert len(probes)==1 and probes[0]['url']=='https://api.example.test/items'
    assert probes[0]['result']['access_result']=='authentication-or-authorization-required'
    assert not detail['findings'];db.db.close()
