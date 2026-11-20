import asyncio
import json
from contextlib import nullcontext
import ssl
import httpx
import pytest
from app.assessment_tools import javascript_evidence,exposure,tls_review,interpret
from app.network import Network,ScopeError
from app.config import SETTINGS,DATA
from app.store import Store
from app.reporting import capture,folder,files,write_report

def response(url,body,status=200,mime='text/plain'):
    return {'url':url,'body':body,'headers':{'content-type':mime},'status':status,'bytes':len(body),'truncated':False}

def test_library_evidence_requires_an_actual_banner_and_remains_candidate():
    result=javascript_evidence(response('https://example.test/jquery-1.12.4.js','/*! jQuery v1.12.4 | jquery.org */\nfetch("/api/items")'))
    assert result['libraries'][0]['version']=='1.12.4'
    assert result['findings'][0]['status']=='candidate' and 'not established' in result['findings'][0]['detail']
    assert not javascript_evidence(response('https://example.test/jquery-1.12.4.js','not jquery'))['findings']
    assert not javascript_evidence(response('https://example.test/jquery.js','/*! jQuery v3.7.1 */'))['findings']

def test_api_mapping_distinguishes_headers_from_http_calls():
    body='const api=axios.create({baseURL:"https://api.example.test"});headers.get("content-type");api.get("/colors");class Users{constructor(){this.BASE="/users";this.all=()=>api.get(this.BASE);}}'
    result=javascript_evidence(response('https://example.test/app.js',body))
    assert result['observed_http_calls']==[{'method':'GET','path':'/colors'}]
    assert result['mapped_get_urls']==['https://api.example.test/colors','https://api.example.test/users']

@pytest.mark.asyncio
async def test_file_exposure_requires_structure_and_a_different_control():
    run={'id':'fixture','url':'https://example.test/','spec':{'max_requests':50},'requests':0}
    class Net:
        body='ref: refs/heads/main\n';same=False
        async def fetch(self,run,url):
            control='.agent24-missing-' in url
            return response(url,self.body if not control or self.same else 'not found',200 if not control or self.same else 404)
    net=Net();action={'url':run['url']+'.git/HEAD'}
    assert (await exposure(action,run,net))['findings'][0]['status']=='confirmed'
    run.pop('_exposure_controls');net.same=True
    assert not (await exposure(action,run,net))['findings']
    run.pop('_exposure_controls');net.same=False;net.body='<html>Welcome to the application</html>'
    assert not (await exposure(action,run,net))['findings']

@pytest.mark.asyncio
async def test_tls_failure_is_verified_without_disabling_validation(monkeypatch):
    error=ssl.SSLCertVerificationError(1,'expired');error.verify_code=10;error.verify_message='certificate has expired'
    class Context:
        def wrap_socket(self,*args,**kwargs):raise error
    async def resolve(*args):return '8.8.8.8'
    monkeypatch.setattr('app.assessment_tools.resolve',resolve)
    monkeypatch.setattr('app.assessment_tools.socket.create_connection',lambda *args,**kwargs:nullcontext(object()))
    monkeypatch.setattr('app.assessment_tools.ssl.create_default_context',lambda:Context())
    run={'url':'https://example.test/','spec':{'max_requests':2},'requests':0}
    result=await tls_review(run,run['url'],SETTINGS)
    assert result['transport']['verify_code']==10 and result['findings'][0]['status']=='confirmed'
    assert run['requests']==1

@pytest.mark.asyncio
async def test_shared_request_budget_survives_concurrent_host_dns(monkeypatch):
    async def resolve(*args):await asyncio.sleep(.01);return '8.8.8.8'
    class Reply:
        status_code=200;headers={}
        async def aiter_bytes(self):yield b'ok'
        async def aclose(self):pass
    class Client:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        def build_request(self,method,url,headers):return httpx.Request(method,url,headers=headers)
        async def send(self,*args,**kwargs):return Reply()
    monkeypatch.setattr('app.network.resolve',resolve);monkeypatch.setattr('app.network.httpx.AsyncClient',Client)
    run={'url':'https://example.test/','spec':{'include_subdomains':True,'max_requests':1},'requests':0}
    net=Network({**SETTINGS,'request_interval':0})
    results=await asyncio.gather(*(net.fetch(run,f'https://{h}.example.test/') for h in ('a','b','c')),return_exceptions=True)
    assert run['requests']==1 and sum(isinstance(r,ScopeError) for r in results)==2

def test_visible_report_manifest_matches_files_and_does_not_execute_html(tmp_path):
    store=Store(tmp_path/'report.sqlite3');run=store.create('https://example.test/','example.test',{})
    value={'response':response(run['url'],'<script>alert(1)</script>',mime='text/html')}
    capture(store,run,'known-artifact',value);result=write_report(store,run['id']);record=files(store,run['id'])[0]
    assert folder(run,store).is_relative_to(DATA/'verification')
    assert record['relative_path'].endswith('.html.txt')
    assert (folder(run,store)/record['relative_path']).read_text()=='<script>alert(1)</script>'
    assert json.loads((folder(run,store)/'files.json').read_text())[0]['sha256']==record['sha256']
    assert result['files']==1;store.db.close()

@pytest.mark.asyncio
async def test_model_cannot_reassign_response_status_or_invent_factual_prose():
    class Model:
        async def generate(self,*args,**kwargs):
            return {'priorities':['public-data-policy'],'analysis':'/users returned HTTP 200 with secret records'}
    baseline=response('https://example.test/colors','["blue","red"]',mime='application/json')
    action={'url':baseline['url'],'data':{'routes':[{'url':'https://example.test/users','status':403}]}}
    result=await interpret(action,baseline,Model())
    assert result['model_selection_valid'] and 'secret records' not in result['analysis']
    assert next(f for f in result['facts'] if f['url'].endswith('/users'))['status']==403
    assert '2 array entries' in result['analysis'] and not result['findings']
    class Invalid:
        async def generate(self,*args,**kwargs):return {'priorities':['invented-exploit']}
    rejected=await interpret(action,baseline,Invalid())
    assert rejected['status']=='partial' and not rejected['recommendations']
