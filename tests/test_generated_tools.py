import json
import time
from types import SimpleNamespace
import pytest
from app.agent_tools import build,supported_urls
from app.deep_assessment import Assessment
from app.engine import normalize_spec


def response(body='<a href="/observed">route</a>'):
    return {'url':'https://example.test/','status':200,'headers':{'content-type':'text/html'},'body':body}


def test_deep_workflow_schedules_real_builder_with_response_inputs():
    run={'id':'test','url':'https://example.test/','_seed_url':'https://example.test/','spec':normalize_spec({'python_analysis':True}),'_deadline':time.monotonic()+60}
    assessment=Assessment(SimpleNamespace(),run,'test');assessment.responses[run['url']]=response()
    candidates=assessment.candidates()
    assert candidates[0]['tool']=='generated_tool'
    assert candidates[0]['data']['inputs']['responses'][0]['body']==response()['body']
    assert not any(c['tool']=='python_analysis' for c in candidates)


def test_generated_leads_need_source_support_scope_and_safe_route():
    inputs={'responses':[response('<a href="/observed">yes</a><a href="https://outside.test/data">outside</a><a href="/logout">logout</a>')]}
    result={'status':'completed','output':{'next_urls':['https://example.test/observed','https://example.test/invented','https://outside.test/data','https://example.test/logout']}}
    run={'url':'https://example.test/','spec':{'include_subdomains':True}}
    assert supported_urls(result,inputs,run)==['https://example.test/observed']
    result['status']='failed'
    assert supported_urls(result,inputs,run)==[]


@pytest.mark.asyncio
async def test_builder_repairs_then_executes_only_after_both_fixture_checks(monkeypatch):
    calls=[];prompts=[]
    class Models:
        async def generate(self,system,data,**kwargs):
            prompts.append(data)
            return 'not valid python !!' if len(prompts)==1 else 'import json\nprint(json.dumps({}))'
    async def sandbox(code,inputs,settings,ident):
        calls.append((ident,inputs))
        urls=[] if not inputs['responses'] else ['https://fixture.invalid/api/example?limit=1'] if '-test' in ident else ['https://example.test/observed']
        return {'status':'completed','stdout':json.dumps({'observations':[],'next_urls':urls}),'sandbox':'test-double'}
    monkeypatch.setattr('app.tools.sandbox_python',sandbox)
    inputs={'responses':[response()]}
    value=await build({'data':{'inputs':inputs}}, {'id':'test'}, Models(), {})
    assert value['status']=='completed' and len(prompts)==2 and prompts[1]['test_feedback']
    assert [i.rsplit('-',1)[-1] for i,_ in calls]==['test','empty','run']
    assert calls[-1][1]==inputs and value['tests'][0]['passed'] is False
    assert value['tests'][1]['passed'] is True


@pytest.mark.asyncio
async def test_invalid_fixture_never_runs_on_real_evidence(monkeypatch):
    calls=[]
    class Models:
        async def generate(self,*args,**kwargs):return 'print("bad")'
    async def sandbox(code,inputs,settings,ident):
        calls.append(ident)
        return {'status':'completed','stdout':'{"observations":[],"next_urls":[]}'}
    monkeypatch.setattr('app.tools.sandbox_python',sandbox)
    value=await build({'data':{'inputs':{'responses':[response()]}}},{'id':'test'},Models(),{})
    assert value['status']=='failed' and len(calls)==2 and all(i.endswith('-test') for i in calls)
