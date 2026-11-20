import asyncio
import json
from pathlib import Path
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import pytest
from fastapi.testclient import TestClient
from app.store import Store,fingerprint
from app.network import normalize,origin,resolve,Network,ScopeError
from app.tools import action_key,execute,surface,sandbox_python
from app.resources import capacity
from app.engine import Engine
from app.api import create_app
from app.config import SETTINGS
from app.models import model_context
from app.models import Models

class FakeModels:
    calls=[]
    async def generate(self,*args,**kwargs):return 'Prioritize the observed surface, response controls and query input differentials.'
    async def choose(self,state,actions):return actions[0],{'choice':'0','probabilities':{'0':1}}
    async def health(self):return {'qwen':{'ready':True,'model_listed':True},'d1':{'ready':True}}

@pytest.fixture
def lab():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body="<html><a href='/search?q=hello'>Search</a><a href='https://outside.invalid/'>External</a></html>"
            if self.path.startswith('/search'):
                from urllib.parse import parse_qs,urlsplit
                value=parse_qs(urlsplit(self.path).query).get('q',[''])[0]
                body='mysql_fetch error SQL syntax MySQL' if "'" in value else 'Search: '+value
            if self.path.startswith('/generic'):
                body='Internal server error';self.send_response(500)
            elif self.path=='/redirect':
                self.send_response(302);self.send_header('Location','https://outside.invalid/');body='redirect'
            else:self.send_response(200)
            self.send_header('Content-Type','text/html')
            if self.headers.get('Origin'):self.send_header('Access-Control-Allow-Origin',self.headers['Origin']);self.send_header('Access-Control-Allow-Credentials','true')
            self.end_headers();self.wfile.write(body.encode())
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{server.server_port}'
    yield url
    server.shutdown();server.server_close()

def config(lab):return {**SETTINGS,'request_interval':0,'request_timeout':2,'local_lab_origins':[lab],'memory_ttl_hours':24,'max_workers':3}
def run(url):return {'id':'test-run','domain':'127.0.0.1','url':url,'requests':0,'spec':{'profile':'lab','max_requests':14,'max_actions':12,'max_seconds':60,'force_retest':False,'continuous':False,'python_analysis':False}}

def test_memory_identity_and_leases(tmp_path):
    store=Store(tmp_path/'test.sqlite3');key=fingerprint({'input':1})
    assert store.claim(key,'lab','tool','run1')[0]=='claimed'
    assert store.claim(key,'lab','tool','run2',force=True)[0]=='leased'
    store.remember(key,'completed',{'marker':'original'})
    assert store.claim(key,'lab','tool','run2')[0]=='cached'
    assert store.claim(key,'lab','tool','run2',force=True)[0]=='claimed'
    store.remember(key,'failed',{'error':'temporary'})
    assert store.claim(key,'lab','tool','run3')[0]=='claimed'
    store.db.close()

def test_changed_data_and_state_are_new_experiments():
    r=run('https://example.com/search?a=1&b=2');baseline={'status':200,'headers':{'date':'one'},'body':'stable'}
    a={'tool':'reflection_probe','url':r['url'],'data':{'marker':'first'}}
    first=action_key(r,a,baseline)
    assert action_key(r,{**a,'url':'https://example.com/search?b=2&a=1'},baseline)==first
    assert action_key(r,{**a,'data':{'marker':'second'}},baseline)!=first
    assert action_key(r,a,{**baseline,'body':'changed'})!=first
    assert action_key(r,a,{**baseline,'headers':{'date':'two'}})==first
    assert action_key(r,a,{**baseline,'headers':{'x-content-type-options':'nosniff'}})!=first
    assert action_key(r,a,{**baseline,'headers':{'set-cookie':'session=random; HttpOnly'}})!=first

def test_scope_and_governor():
    assert normalize('EXAMPLE.com:443/a#fragment')=='https://example.com/a'
    for url in ['file:///etc/passwd','http://user:pass@example.com','https://example.com\\bad']:
        with pytest.raises(ScopeError):normalize(url)
    assert capacity({'ram_available_gb':.5},3)[0]==0
    assert capacity({'ram_available_gb':9,'gpu':{'temperature':84,'used_mb':7000,'total_mb':8000}},3)[0]==1
    assert capacity({'ram_available_gb':5},3)[0]==2

def test_large_model_context_remains_valid_json():
    payload={'goal':'Assess supplied lab','sources':[{'body':'x'*30000,'links':['https://example.com/'+'a'*2000]*40}]*50}
    encoded=model_context(payload)
    assert len(encoded)<14000 and isinstance(json.loads(encoded),dict)

@pytest.mark.asyncio
async def test_transient_model_error_is_retried_once(monkeypatch):
    import httpx
    calls=[]
    class Client:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,json):
            calls.append(json)
            return httpx.Response(500 if len(calls)==1 else 200,request=httpx.Request('POST',url),json={'error':'fixture: transient'} if len(calls)==1 else {'output':[{'type':'message','content':'A bounded plan.'}],'stats':{}})
    monkeypatch.setattr('app.models.httpx.AsyncClient',Client)
    model=Models(SETTINGS)
    assert await model.generate('Plan',{'goal':'Lab'},raw=True)=='A bounded plan.'
    assert len(calls)==2 and model.calls[-1]['recovered']

@pytest.mark.asyncio
async def test_private_dns_and_redirect_boundary(lab):
    with pytest.raises(ScopeError):await resolve(lab)
    net=Network(config(lab));r=run(lab+'/redirect');result=await net.fetch(r,r['url'])
    assert result['redirect_blocked']=='https://outside.invalid/'
    assert r['requests']==1
    with pytest.raises(ScopeError):await net.fetch(r,'https://outside.invalid/')

@pytest.mark.asyncio
async def test_candidate_evidence_not_false_confirmation(lab):
    cfg=config(lab);net=Network(cfg);r=run(lab+'/search?q=hello');baseline=await net.fetch(r,r['url'])
    result=await execute({'tool':'database_error_probe','url':r['url']},r,baseline,net,FakeModels(),cfg)
    assert result['findings'][0]['status']=='candidate'
    r=run(lab+'/generic?q=hello');baseline=await net.fetch(r,r['url'])
    result=await execute({'tool':'database_error_probe','url':r['url']},r,baseline,net,FakeModels(),cfg)
    assert not result['findings'] # Generic 500 must not become SQLi.
    reflected=await execute({'tool':'reflection_probe','url':lab+'/search?q=hello'},r,baseline,net,FakeModels(),cfg)
    assert reflected['reflected'] and not reflected['findings'] # Reflection is not XSS.

@pytest.mark.asyncio
async def test_cookie_values_do_not_masquerade_as_attributes():
    baseline={'headers':{'set-cookie':'session=secure_httponly_samesite; Path=/; SameSite=Lax'}}
    result=await execute({'tool':'cookie_review'},run('https://example.com/'),baseline,None,None,SETTINGS)
    assert not result['secure'] and not result['httponly'] and result['samesite']
    baseline['headers']['set-cookie']='session=abc; Secure; HttpOnly; SameSite=Strict'
    result=await execute({'tool':'cookie_review'},run('https://example.com/'),baseline,None,None,SETTINGS)
    assert result['secure'] and result['httponly'] and result['samesite']

@pytest.mark.asyncio
async def test_real_requests_memory_reuse_and_force(tmp_path,lab):
    store=Store(tmp_path/'engine.sqlite3');engine=Engine(store,config(lab),FakeModels());engine.slots=2
    spec=run(lab+'/')['spec']
    first=store.create(lab+'/','127.0.0.1',spec);await engine.assess(first['id'],'w1')
    first_detail=store.detail(first['id']);assert first_detail['status']=='completed'
    assert any(x['kind']=='dispatch' for x in first_detail['events'])
    assert first_detail['findings'] and all(x['status']=='candidate' for x in first_detail['findings'])
    second=store.create(lab+'/','127.0.0.1',spec);await engine.assess(second['id'],'w2')
    second_detail=store.detail(second['id']);assert sum(a['status']=='reused' for a in second_detail['actions'])>=5
    assert second_detail['requests']==1
    third=store.create(lab+'/','127.0.0.1',{**spec,'force_retest':True});await engine.assess(third['id'],'w3')
    assert not any(a['status']=='reused' for a in store.detail(third['id'])['actions'])
    store.db.close()

def test_restart_preserves_history_and_clears_leases(tmp_path):
    store=Store(tmp_path/'recover.sqlite3');r=store.create('https://example.com/','example.com',{})
    store.claim('key','example.com','tool',r['id']);store.update(r['id'],status='running');store.recover()
    assert store.run(r['id'])['status']=='interrupted'
    assert store.rows('SELECT lease_until FROM memory')[0]['lease_until']==0
    assert store.detail(r['id'])['events'][-1]['kind']=='recovery';store.db.close()

def test_user_pause_survives_recovery(tmp_path):
    store=Store(tmp_path/'paused.sqlite3');r=store.create('https://example.com/','example.com',{'continuous':True})
    store.update(r['id'],status='paused');store.recover();assert store.run(r['id'])['status']=='paused';store.db.close()

@pytest.mark.asyncio
async def test_scheduler_stop_preserves_completed_result(tmp_path):
    store=Store(tmp_path/'schedule.sqlite3');engine=Engine(store,SETTINGS,FakeModels())
    r=store.create('https://example.com/','example.com',{'continuous':True})
    store.update(r['id'],status='completed',next_due=9999999999)
    await engine.control(r['id'],'stop')
    assert store.run(r['id'])['status']=='completed' and store.run(r['id'])['next_due']==0
    store.db.close()

@pytest.mark.asyncio
async def test_resume_after_restart_reobserves(tmp_path):
    store=Store(tmp_path/'resume.sqlite3');engine=Engine(store,SETTINGS,FakeModels())
    r=store.create('https://example.com/','example.com',{'continuous':True});store.update(r['id'],status='paused')
    replacement=await engine.control(r['id'],'resume')
    assert replacement['id']!=r['id'] and engine.queue.qsize()==1
    store.db.close()

@pytest.mark.asyncio
async def test_autonomous_mission_uses_standard_loop_without_crashing(tmp_path):
    from app.missions import attach
    store=Store(tmp_path/'autonomous.sqlite3');engine=Engine(store,SETTINGS,FakeModels())
    r=store.create('https://example.com/','example.com',{'continuous':True,'autonomous':True,'mission_id':'mission-1','max_requests':8,'max_actions':8,'max_seconds':60})
    attach(engine,r)
    result=await engine.assess(r['id'],'worker-1')
    assert result is not None
    assert store.run(r['id'])['spec']['autonomous'] is False
    assert store.rows('SELECT * FROM missions WHERE id=?',('mission-1',))[0]['active_run']==r['id']
    store.db.close()

@pytest.mark.asyncio
async def test_autonomous_mission_persists_state_and_logs_synthesis(tmp_path,lab):
    """Mission state is saved after each cycle so the next cycle inherits it."""
    from app.missions import attach
    from app.agent_loop import _load
    store=Store(tmp_path/'state.sqlite3');engine=Engine(store,config(lab),FakeModels())
    r=store.create(lab+'/','127.0.0.1',{'continuous':True,'autonomous':True,'mission_id':'m-persist','max_requests':14,'max_actions':18,'max_seconds':60})
    attach(engine,r)
    result=await engine.assess(r['id'],'worker-1')
    assert result is not None
    state=_load(engine,'m-persist')
    # Surface map must be populated after observing the lab host.
    assert '127.0.0.1' in state['surface']
    # At least one mission event must be recorded.
    events=store.rows("SELECT * FROM events WHERE run_id=? AND kind='mission'",(r['id'],))
    assert events,'Expected at least one mission event'
    # State must be written to the agent_state table.
    rows=store.rows('SELECT state FROM agent_state WHERE mission_id=?',('m-persist',))
    assert rows,'agent_state table must have an entry for the mission'
    store.db.close()

def test_api_state_exposes_missions(tmp_path,lab):
    """The /api/state response must include the missions list."""
    store=Store(tmp_path/'apistate.sqlite3');application=create_app(config(lab),store,FakeModels())
    with TestClient(application) as client:
        state=client.get('/api/state').json()
        assert 'missions' in state,'missions key missing from /api/state'
    store.db.close()

@pytest.mark.asyncio
async def test_independent_jobs_overlap_and_cancel_worker_recovers(tmp_path,monkeypatch):
    import app.engine as engine_module
    async def resources():return {'ram_available_gb':5,'ram_percent':50}
    monkeypatch.setattr(engine_module,'measure',resources)
    class SlowNetwork:
        active=0;peak=0
        async def fetch(self,r,url,headers=None,method='GET'):
            self.active+=1;self.peak=max(self.peak,self.active)
            try:await asyncio.sleep(.08)
            finally:self.active-=1
            r['requests']+=1
            return {'url':url,'status':200,'headers':{},'body':'<html></html>','bytes':13,'method':'GET'}
    store=Store(tmp_path/'workers.sqlite3');network=SlowNetwork();engine=Engine(store,SETTINGS,FakeModels(),network)
    await engine.start()
    try:
        spec=run('https://one.example/')['spec']
        one=await engine.submit('https://one.example/','one.example',spec)
        two=await engine.submit('https://two.example/','two.example',spec)
        await asyncio.wait_for(engine.queue.join(),5)
        assert network.peak>=2 and store.run(one['id'])['status']=='completed' and store.run(two['id'])['status']=='completed'
        three=await engine.submit('https://three.example/','three.example',spec)
        await asyncio.sleep(.02);await engine.control(three['id'],'stop');await asyncio.wait_for(engine.queue.join(),5)
        assert store.run(three['id'])['status']=='cancelled'
        four=await engine.submit('https://four.example/','four.example',spec);await asyncio.wait_for(engine.queue.join(),5)
        assert store.run(four['id'])['status']=='completed'
    finally:await engine.close();store.db.close()

@pytest.mark.asyncio
async def test_python_does_not_fall_back_to_host(monkeypatch,tmp_path):
    monkeypatch.setattr('app.tools.shutil.which',lambda name:None)
    async def safe_worker(code,inputs,settings):return {'status':'blocked','reason':'fixture: no sandbox'}
    monkeypatch.setattr('app.python_sandbox.run_python',safe_worker)
    result=await sandbox_python('raise RuntimeError("must not run")',{},SETTINGS,'test')
    assert result['status']=='blocked'

def test_api_origin_auth_and_registry(tmp_path,lab):
    store=Store(tmp_path/'api.sqlite3');app=create_app(config(lab),store,FakeModels())
    with TestClient(app) as client:
        assert client.post('/api/runs',json={'url':lab}).status_code==403
        session=client.get('/api/session').json();headers={'X-Agent24-Token':session['token']}
        assert client.post('/api/runs',headers={**headers,'Origin':'https://outside.invalid'},json={'url':lab}).status_code==403
        assert client.post('/api/runs',headers=headers,json={'url':'https://portswigger.net/web-security/'}).status_code==400
        assert client.get('/api/skills?q=ssrf').json()['matches']>0
        response=client.post('/api/runs',headers=headers,json={'url':lab,'max_requests':4});assert response.status_code==200
        ident=response.json()['id'];assert client.get('/api/runs/'+ident).status_code==200
        assert client.get('/api/runs/'+ident+'/export/report').headers['content-type']=='application/zip'
    store.db.close()
