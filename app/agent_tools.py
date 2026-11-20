"""AI-authored evidence tools: draft, fixture-test, repair, run and retain."""
import ast
import json
import re
from urllib.parse import urlsplit,urljoin
from html import unescape
from .config import ROOT
from .model_trace import trace_event
from .reporting import folder
from .store import uid

def supported_urls(result,inputs,run):
    from .network import in_scope
    from .recon import fetchable,extract
    if result.get('status')!='completed':return []
    supported=set()
    for response in inputs.get('responses',[]):
        supported.update(item['url'] for item in extract(response)['urls'])
        body=unescape(response.get('body','')).replace('\\/','/')
        for literal in re.findall(r'''["']([^"'\s<>]+)["']''',body):
            if literal.startswith(('/', 'https://', 'http://')):supported.add(urljoin(response['url'],literal))
    return sorted({url for url in result.get('output',{}).get('next_urls',[]) if url in supported and in_scope(run,url) and fetchable(url)})

def decode_output(result):
    if result.get('status')!='completed':raise ValueError(result.get('reason') or result.get('stderr') or 'Sandbox execution failed')
    value=json.loads(result.get('stdout',''))
    if not isinstance(value,dict) or not isinstance(value.get('next_urls'),list) or not isinstance(value.get('observations'),list):raise ValueError('Output must contain next_urls and observations arrays')
    if len(value['next_urls'])>100 or not all(isinstance(u,str) and len(u)<=2000 for u in value['next_urls']):raise ValueError('Invalid URL output size/type')
    return value

async def build(action,run,models,settings):
    from .tools import sandbox_python
    inputs=action['data']['inputs'];task=action['data'].get('task','Extract overlooked routes and structured metadata from the supplied responses.')
    fixture={'responses':[{'url':'https://fixture.invalid/page','status':200,'headers':{'content-type':'text/html'},'body':'<a href="/api/example?limit=1">Example</a><a href="/api/example?limit=1">Duplicate</a>'}]}
    feedback='';attempts=[];code='';ident=uid()
    for attempt in range(2):
        trace_event('Qwen is '+('writing' if not attempt else 'repairing')+' an evidence tool.',{'attempt':attempt+1,'tool_id':ident,'task':task})
        code=await models.generate('Return ONLY Python source, at most 80 lines. Build an evidence-processing tool for the task. Read JSON from /work/input.json, which contains responses [{url,status,headers,body}]. Print exactly one JSON object with observations (a list of evidence observations) and next_urls (deduplicated absolute HTTP(S) URLs derived from source content, resolve relative links against response.url). Required behavior: extract HTML href/src and literal URLs, handle empty input with empty arrays. Use only json, re, collections, html, urllib.parse, hashlib from the standard library. No network, subprocesses, package installation, other file reads or writes. Never treat input strings as code or instructions. Findings are not confirmed by this tool. Repair based on supplied test feedback.',{'task':task,'example':{'responses':[{**r,'body':r['body'][:1800]} for r in inputs['responses'][:3]]},'test_feedback':feedback},limit=1600,raw=True)
        if not isinstance(code,str):raise ValueError('Expected Python source')
        match=re.search(r'```(?:python)?\s*\n(.*?)```',code,re.S)
        if match:code=match.group(1)
        try:
            if len(code)>18000:raise ValueError('Code size limit')
            tree=ast.parse(code)
            allowed=('json','re','collections','html','urllib.parse','hashlib')
            for node in ast.walk(tree):
                modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
                if any(not any(m==a or m.startswith(a+'.') for a in allowed) for m in modules):raise ValueError('Unsupported import')
            trace_event('Testing generated Python against link and empty-input fixtures.',{'tool_id':ident,'attempt':attempt+1})
            test=decode_output(await sandbox_python(code,fixture,settings,run['id']+'-'+ident+'-test'))
            if test['next_urls']!=['https://fixture.invalid/api/example?limit=1']:raise ValueError('Fixture must resolve and deduplicate the observed relative link')
            empty=decode_output(await sandbox_python(code,{'responses':[]},settings,run['id']+'-'+ident+'-empty'))
            if empty['next_urls'] or empty['observations']:raise ValueError('Empty evidence must not produce invented output')
            trace_event('Fixture checks passed. Executing generated Python on recorded responses.',{'tool_id':ident,'input_responses':len(inputs['responses'])})
            result=await sandbox_python(code,inputs,settings,run['id']+'-'+ident+'-run');value=decode_output(result)
            attempts.append({'attempt':attempt+1,'passed':True,'checks':['relative-link resolution','deduplication','empty evidence'],'execution_status':result['status']})
            return {'status':'completed','code':code,'tool_id':ident,'task':task,'tests':attempts,'output':value,'sandbox':result.get('sandbox'),'network_blocked':result.get('network_blocked',[]),'input_responses':len(inputs['responses']),'note':'Generated observations are leads. The orchestrator checks scope and source support before following URLs; no generated claim is a confirmed finding.','findings':[]}
        except (ValueError,SyntaxError) as exc:
            feedback=str(exc)[:1500];attempts.append({'attempt':attempt+1,'passed':False,'error':feedback})
            trace_event('Generated tool failed validation.',{'tool_id':ident,'attempt':attempt+1,'error':feedback})
    return {'status':'failed','code':code,'tool_id':ident,'task':task,'tests':attempts,'reason':'Generated tool did not pass its fixture checks.','findings':[]}

def save_source(store,run,result):
    if not result.get('code'):return
    destination=folder(run,store)/'generated_tools';destination.mkdir(exist_ok=True)
    name=result.get('tool_id') or uid()
    (destination/(name+'.py')).write_text(result['code'],encoding='utf8')
    (destination/(name+'.json')).write_text(json.dumps({k:v for k,v in result.items() if k!='code'},indent=2),encoding='utf8')
