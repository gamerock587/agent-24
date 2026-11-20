import asyncio
import json
import time
import httpx
import pytest
from fastapi.testclient import TestClient
from app.api import create_app
from app.config import SETTINGS
from app.model_trace import redact,trace_context,traced_post
from app.store import Store
from app.live_chat import transcript
from app.chat_readable import exchange


def test_readable_messages_support_both_qwen_adapters_and_liquid():
    native=exchange({'input':json.dumps({'system_prompt':'Be helpful','input':json.dumps({'conversation':[{'role':'user','content':'hello'}]})}),'output':json.dumps({'body':json.dumps({'output':[{'type':'message','content':'Hi there!'}]})})})
    assert native['received']=='Hi there!' and 'hello' in native['sent'][1]['text']
    standard=exchange({'input':json.dumps({'messages':[{'role':'user','content':'hello'}]}),'output':json.dumps({'body':json.dumps({'choices':[{'message':{'content':'Hello!'}}]})})})
    assert standard['sent'][0]['text']=='hello' and standard['received']=='Hello!'
    liquid=exchange({'input':json.dumps({'state':{'target':'example.test'},'questions':{'next':{'criteria':{'0':'Check headers'}}}}),'output':json.dumps({'body':json.dumps({'answers':{'next':{'choice':'0','probabilities':{'0':1}}}})})})
    assert 'Check headers' in liquid['sent'][0]['text'] and 'Choice' in liquid['received']


def test_model_filter_applies_before_pagination(tmp_path):
    db=Store(tmp_path/'filter.db');run=db.create('https://example.test/','example.test',{})
    for index in range(70):
        db.execute('INSERT INTO model_turns VALUES(?,?,?,?,?,?,?,?,?)',(str(index),run['id'],'Qwen3.5 9B' if index==0 else 'Liquid d1','test','completed','{}','{}',index+1,index+2))
    result=transcript(db,run['id'],model='qwen')
    assert len(result['turns'])==1 and result['turns'][0]['model']=='Qwen3.5 9B'
    assert not result['has_older']
    db.db.close()


@pytest.mark.asyncio
async def test_greeting_does_not_send_unrelated_failure_records(tmp_path):
    from types import SimpleNamespace
    from app.live_chat import answer
    db=Store(tmp_path/'greet.db');run=db.create('https://example.test/','example.test',{})
    db.update(run['id'],status='failed',summary='ConnectTimeout')
    class Models:
        async def generate(self,system,data,**kwargs):
            assert data=={'conversation':[{'role':'user','content':'hi'}]}
            return 'Hi! How can I help?'
    await answer(SimpleNamespace(store=db,models=Models()),run['id'],'hi')
    assert db.rows('SELECT content FROM messages')[0]['content']=='Hi! How can I help?'
    db.db.close()

def test_nested_wire_json_redacts_secrets_without_changing_plain_text():
    value={'input':json.dumps({'access_token':'private-token','text':'ordinary message','nested':{'password':'secret-value'}}),'authorization':'Bearer abc'}
    result=redact(value);encoded=json.dumps(result)
    assert 'private-token' not in encoded and 'secret-value' not in encoded and 'ordinary message' in encoded

def test_old_model_calls_remain_accessible_without_mixing_targets(tmp_path):
    db=Store(tmp_path/'pages.db');run=db.create('https://example.test/','example.test',{})
    for index in range(65):
        db.execute('INSERT INTO model_turns VALUES(?,?,?,?,?,?,?,?,?)',(str(index),run['id'],'Qwen','test','completed','{}','{}',index+1,index+2))
    latest=transcript(db,run['id']);older=transcript(db,run['id'],latest['turns'][0]['created'])
    assert latest['has_older'] and len(latest['turns'])==60
    assert not older['has_older'] and len(older['turns'])==5
    assert len({t['id'] for t in latest['turns']+older['turns']})==65
    db.db.close()

@pytest.mark.asyncio
async def test_traces_keep_concurrent_model_exchanges_with_the_correct_run(tmp_path):
    db=Store(tmp_path/'traces.db')
    class Client:
        async def post(self,url,json,**kwargs):
            await asyncio.sleep(.01)
            return httpx.Response(200,json={'echo':json['value']})
    async def call(run,value):
        with trace_context(db,run,'test'):
            return await traced_post(Client(),'http://local.test',{'value':value},'Qwen')
    await asyncio.gather(call('one','first'),call('two','second'))
    rows=db.rows('SELECT * FROM model_turns ORDER BY created')
    assert len(rows)==2 and all(r['status']=='completed' for r in rows)
    for row in rows:
        assert json.loads(json.loads(row['output'])['body'])['echo']==json.loads(row['input'])['value']
    assert {r['run_id'] for r in rows}=={'one','two'}
    db.db.close()

def test_chat_is_persisted_uses_actual_reply_and_does_not_execute_target_requests(tmp_path):
    db=Store(tmp_path/'chat.db');run=db.create('https://example.test/','example.test',{})
    db.update(run['id'],status='completed')
    class Models:
        calls=[]
        async def health(self):return {'qwen':{'ready':True},'d1':{'ready':True}}
        async def generate(self,system,data,**kwargs):
            assert data['conversation'][-1]['content']=='What happened?'
            return 'No assessment requests have been recorded.'
    class Network:
        async def fetch(self,*args,**kwargs):raise AssertionError('Chat must not run HTTP probes')
    with TestClient(create_app(settings=SETTINGS,store=db,models=Models(),network=Network())) as client:
        token=client.get('/api/session').json()['token'];url='/api/runs/'+run['id']+'/chat'
        assert client.post(url,json={'content':'What happened?'}).status_code==403
        assert client.post(url,json={'content':'What happened?'},headers={'X-Agent24-Token':token}).status_code==200
        for _ in range(20):
            result=client.get(url).json()
            if len(result['messages'])==2:break
            time.sleep(.01)
        assert [m['role'] for m in result['messages']]==['user','assistant']
        assert result['messages'][-1]['content']=='No assessment requests have been recorded.'
        assert not result['turns'] # Fake model must not produce invented trace rows.
        assert client.get('/api/runs/nonexistent/chat').status_code==404
        assert client.post(url,json={'content':' '},headers={'X-Agent24-Token':token}).status_code==400
    db.db.close()
