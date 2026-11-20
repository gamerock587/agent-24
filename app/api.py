import asyncio
from contextlib import asynccontextmanager
import io
import json
from pathlib import Path
import secrets
import time
import zipfile
from urllib.parse import urlsplit
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import FileResponse,StreamingResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .config import ROOT,DATA,SETTINGS
from .store import Store,canonical
from .network import normalize,resolve,ScopeError
from .engine import Engine
from .tools import TOOLS

class RunSpec(BaseModel):
    url:str=Field(min_length=3,max_length=2000)
    profile:str='lab'
    deep:bool=True
    include_subdomains:bool=True
    file_checks:bool=True
    analyze_evidence:bool=True
    parameter_probes:bool=True
    continue_from:str|None=None
    review_from:str|None=None
    force_retest:bool=False
    continuous:bool=False
    python_analysis:bool=False
    autonomous:bool=False
    objective:str=Field(default='Investigate the observed attack surface, validate plausible findings, and explain coverage gaps.',max_length=2000)
    cycle_delay:int=Field(default=20,ge=5,le=3600)
    idle_delay:int=Field(default=900,ge=60,le=86400)
    max_requests:int=Field(default=120,ge=1,le=1000)
    max_actions:int=Field(default=180,ge=2,le=1500)
    max_seconds:int=Field(default=900,ge=30,le=7200)
    max_pages:int=Field(default=50,ge=1,le=500)
    crawl_depth:int=Field(default=4,ge=0,le=10)
    max_hosts:int=Field(default=8,ge=1,le=40)
    max_dns_queries:int=Field(default=64,ge=1,le=256)
    max_parameters:int=Field(default=4,ge=1,le=20)

class ChatMessage(BaseModel):
    content:str=Field(min_length=1,max_length=4000)

def create_app(settings=None,store=None,models=None,network=None):
    cfg={**SETTINGS,**(settings or {})};db=store or Store();engine=Engine(db,cfg,models,network);token=secrets.token_urlsafe(32)
    @asynccontextmanager
    async def lifespan(app):
        await engine.start()
        try:yield
        finally:await engine.close()
    app=FastAPI(title='Agent 24',lifespan=lifespan);app.state.engine=engine;app.state.store=db
    @app.middleware('http')
    async def protect(request,call_next):
        host=request.headers.get('host','').split(':')[0]
        if host not in ('127.0.0.1','localhost','testserver'):
            return JSONResponse({'detail':'Local host only'},status_code=403)
        if request.url.path.startswith('/api/'):
            source=request.headers.get('origin')
            if source and source not in (f'http://127.0.0.1:{cfg["port"]}',f'http://localhost:{cfg["port"]}'):
                return JSONResponse({'detail':'Foreign origin rejected'},status_code=403)
            if request.method!='GET' and request.headers.get('x-agent24-token')!=token:
                return JSONResponse({'detail':'Session token required'},status_code=403)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        if request.url.path in ('/sandbox','/static/python-worker.js','/static/python-host.js') or request.url.path.startswith('/python-runtime/'):
            response.headers['Content-Security-Policy']="default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; worker-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        return response
    @app.get('/api/session')
    async def session():return {'app':'Agent 24','token':token,'version':'0.1.0'}
    @app.get('/api/state')
    async def state():
        runs=db.rows('SELECT id,domain,url,status,created,updated,summary,requests,next_due FROM runs ORDER BY created DESC LIMIT 200')
        history=db.rows('SELECT domain,COUNT(*) runs,MAX(updated) updated FROM runs GROUP BY domain ORDER BY updated DESC')
        stats=db.rows('SELECT status,COUNT(*) count FROM memory GROUP BY status')
        missions=db.rows('SELECT id,domain,url,status,active_run,next_due,cycles,summary,updated FROM missions ORDER BY updated DESC LIMIT 40')
        return {'runs':runs,'history':history,'missions':missions,'resources':engine.metrics,'worker_capacity':engine.slots,'resource_reason':engine.resource_reason,'workers':[{k:v for k,v in value.items() if k!='task'}|{'run_id':ident} for ident,value in engine.running.items()],'tool_workers':list(engine.active_tools.values()),'model_activity':db.rows("SELECT id,model,purpose,status,created,finished FROM model_turns WHERE status='running' OR finished>? ORDER BY created DESC LIMIT 12",(time.time()-3,)),'models':engine.health,'model_calls':engine.models.calls[-20:],'memory':stats,'queue_size':engine.queue.qsize()}
    @app.post('/api/runs')
    async def submit(spec:RunSpec):
        if spec.profile not in ('observe','lab'):raise HTTPException(400,'Choose observe or lab profile.')
        try:
            url=normalize(spec.url);host=urlsplit(url).hostname
            if host in ('portswigger.net','www.portswigger.net','picoctf.org','www.picoctf.org','github.com','www.github.com','owasp.org'):
                raise ScopeError('This is a documentation/platform host. Supply a generated challenge instance or your own deployed target.')
            await resolve(url,cfg['local_lab_origins'])
        except (ValueError,OSError) as exc:raise HTTPException(400,str(exc))
        active=db.rows("SELECT id FROM runs WHERE domain=? AND status IN ('queued','running','paused')",(host,))
        if active:raise HTTPException(409,'This domain already has an active assessment. Stop it or wait before retesting.')
        value=spec.model_dump();value.pop('url');return await engine.submit(url,host,value)
    @app.get('/api/runs/{ident}')
    async def detail(ident:str):
        try:return db.detail(ident)
        except KeyError:raise HTTPException(404,'Unknown assessment')
    @app.get('/api/runs/{ident}/files')
    async def captured_files(ident:str):
        from .reporting import files,folder
        try:run=db.run(ident)
        except KeyError:raise HTTPException(404,'Unknown assessment')
        analyses=db.rows("SELECT tool,url,status,result FROM actions WHERE run_id=? AND tool IN ('javascript_review','evidence_analysis','tls_certificate_review','file_exposure_probe','api_inventory','api_route_probe')",(ident,))
        for item in analyses:item['result']=json.loads(item['result'])
        return {'files':files(db,ident),'analysis':analyses,'folder':str(folder(run,db))}
    @app.get('/api/runs/{ident}/chat')
    async def chat_history(ident:str,before:float|None=None,model:str|None=None):
        from .live_chat import transcript
        try:return transcript(db,ident,before,model)
        except KeyError:raise HTTPException(404,'Unknown assessment')
    @app.post('/api/runs/{ident}/chat')
    async def chat_send(ident:str,message:ChatMessage):
        from .live_chat import chat_scope,answer
        from .model_trace import redact
        from .store import uid
        try:run,scope=chat_scope(db,ident)
        except KeyError:raise HTTPException(404,'Unknown assessment')
        content=message.content.strip()
        if not content:raise HTTPException(400,'Write a message first.')
        if any(getattr(task,'chat_scope',None)==scope for task in engine.chat_tasks):raise HTTPException(409,'Wait for the current chat reply.')
        if len(engine.chat_tasks)>=3:raise HTTPException(429,'The local model chat queue is full. Try again after a reply.')
        mid=uid();db.execute('INSERT INTO messages VALUES(?,?,?,?,?,?)',(mid,scope,ident,'user',str(redact(content)),time.time()))
        task=asyncio.create_task(answer(engine,ident,content));task.chat_scope=scope
        engine.chat_tasks.add(task);task.add_done_callback(engine.chat_tasks.discard)
        return {'id':mid,'status':'queued'}
    @app.get('/api/model-turns/{turn_id}')
    async def model_turn(turn_id:str):
        rows=db.rows('SELECT * FROM model_turns WHERE id=?',(turn_id,))
        if not rows:raise HTTPException(404,'Unknown model call')
        value=rows[0];value['input']=json.loads(value['input']);value['output']=json.loads(value['output']) if value['output'] else None
        return value
    @app.get('/api/runs/{ident}/files/{artifact}')
    async def download_file(ident:str,artifact:str):
        from .reporting import folder
        rows=db.rows('SELECT * FROM captured_files WHERE run_id=? AND id=?',(ident,artifact))
        if not rows:raise HTTPException(404,'Unknown captured response')
        base=folder(db.run(ident),db);path=(base/rows[0]['relative_path']).resolve()
        if not path.is_relative_to(base.resolve()):raise HTTPException(403,'Invalid report path')
        return FileResponse(path,media_type='application/octet-stream',filename=path.name)
    @app.post('/api/runs/{ident}/{action}')
    async def control(ident:str,action:str):
        try:return await engine.control(ident,action)
        except KeyError:raise HTTPException(404,'Unknown assessment')
        except ValueError as e:raise HTTPException(400,str(e))
    @app.get('/api/evidence/{ident}')
    async def evidence(ident:str):
        records=db.rows('SELECT * FROM artifacts WHERE id=?',(ident,))
        if not records:raise HTTPException(404,'Unknown evidence')
        record=records[0];path=Path(record['path']).resolve()
        if not path.is_relative_to(DATA/'evidence'):raise HTTPException(403,'Invalid evidence path')
        return {'id':ident,'name':record['name'],'sha256':record['sha256'],'bytes':record['bytes'],'content':path.read_text(encoding='utf8')}
    @app.get('/api/missions')
    async def missions_list():
        rows=db.rows('SELECT id,domain,url,status,active_run,next_due,cycles,summary,updated FROM missions ORDER BY updated DESC LIMIT 100')
        return {'missions':rows}
    @app.get('/api/missions/{mid}')
    async def mission_detail(mid:str):
        rows=db.rows('SELECT * FROM missions WHERE id=?',(mid,))
        if not rows:raise HTTPException(404,'Unknown mission')
        m=rows[0];m['spec']=json.loads(m['spec'])
        state_rows=db.rows('SELECT state,updated FROM agent_state WHERE mission_id=?',(mid,))
        m['agent_state']=json.loads(state_rows[0]['state']) if state_rows else {}
        run_ids=db.rows("SELECT id FROM runs WHERE json_extract(spec,'$.mission_id')=? ORDER BY created DESC LIMIT 20",(mid,))
        m['run_ids']=[r['id'] for r in run_ids]
        return m
    @app.post('/api/missions/{mid}/{action}')
    async def mission_control(mid:str,action:str):
        rows=db.rows('SELECT * FROM missions WHERE id=?',(mid,))
        if not rows:raise HTTPException(404,'Unknown mission')
        m=rows[0]
        try:return await engine.control(m['active_run'],action)
        except KeyError:raise HTTPException(404,'Unknown mission run')
        except ValueError as e:raise HTTPException(400,str(e))
    @app.get('/api/skills')
    async def skills(q:str='',limit:int=40):
        catalog=json.loads((ROOT/'registry/all-skills.json').read_text(encoding='utf8'))
        words=q.lower().split();matches=[s for s in catalog if all(w in (s['name']+' '+s['description']).lower() for w in words)]
        enabled={v[1] for v in TOOLS.values()}
        matches.sort(key=lambda x:(x['repo']!='Agent 24 original drafts',x['name']))
        return {'total':len(catalog),'matches':len(matches),'skills':[{'id':s['id'],'name':s['name'],'description':s['description'],'status':'registered workflow' if s['id'].startswith('agent24:') and s['name'] in enabled else s['status']} for s in matches[:min(100,max(1,limit))]],'tools':[{'id':k,'title':v[0],'skill':v[1],'description':v[2]} for k,v in TOOLS.items()]}
    @app.get('/api/memory')
    async def memory(domain:str=''):
        rows=db.rows('SELECT fingerprint,domain,tool,status,last_test,attempts,lease_until FROM memory '+('WHERE domain=? ' if domain else '')+'ORDER BY last_test DESC LIMIT 250',(domain,) if domain else ())
        return {'entries':rows,'ttl_hours':cfg['memory_ttl_hours'],'note':'Identity includes URL, sorted query data, tool version, profile and baseline response hash.'}
    @app.get('/api/scenarios')
    async def scenarios(q:str=''):
        path=ROOT/'test-scenarios.json'
        data=json.loads(path.read_text(encoding='utf8')) if path.exists() else {'scenarios':[]}
        return {'notes':data.get('notes',[]),'scenarios':[s for s in data['scenarios'] if q.lower() in (s['scenario']+' '+s['url']).lower()][:200]}
    @app.get('/api/runs/{ident}/export/report')
    async def export(ident:str):
        try:result=db.detail(ident)
        except KeyError:raise HTTPException(404,'Unknown assessment')
        # Reports include compact, cookie-redacted outcomes; raw evidence stays local.
        stream=io.BytesIO()
        from .reporting import folder,write_report
        if result.get('coverage'):
            write_report(db,ident);base=folder(result,db)
            with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
                for path in base.rglob('*'):
                    if path.is_file():z.write(path,path.relative_to(base).as_posix())
            return StreamingResponse(iter([stream.getvalue()]),media_type='application/zip',headers={'Content-Disposition':f'attachment; filename="agent24-{ident}.zip"'})
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.json',json.dumps(result,indent=2))
            lines=['# Agent 24 assessment',f'Target: {result["url"]}',f'Status: {result["status"]}',result['summary'],'','## Findings']
            for finding in result['findings']:lines.extend([f'### {finding["title"]}',f'Status: {finding["status"]}',finding['detail'],f'Evidence IDs: {finding["evidence"]}'])
            lines+=['','Raw evidence remains in the local evidence store. Candidates are not confirmed vulnerabilities.']
            z.writestr('report.md','\n\n'.join(lines))
        return StreamingResponse(iter([stream.getvalue()]),media_type='application/zip',headers={'Content-Disposition':f'attachment; filename="agent24-{ident}.zip"'})
    (ROOT/'.runtime/python-wasm').mkdir(parents=True,exist_ok=True)
    app.mount('/python-runtime',StaticFiles(directory=ROOT/'.runtime/python-wasm'),name='python-runtime')
    @app.get('/sandbox')
    async def sandbox():
        from fastapi.responses import HTMLResponse
        return HTMLResponse('<!doctype html><html><head><script src="/static/python-host.js"></script></head><body></body></html>')
    app.mount('/static',StaticFiles(directory=ROOT/'web'),name='static')
    @app.get('/')
    async def index():return FileResponse(ROOT/'web/index.html')
    return app

