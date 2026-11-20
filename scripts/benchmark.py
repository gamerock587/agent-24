"""Behavior benchmarks: controlled local fixture with real models, or bounded public observations."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import parse_qs,urlsplit
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import SETTINGS,DATA
from app.store import Store
from app.engine import Engine
from app.resources import measure,capacity

DEST=DATA/'verification';DEST.mkdir(parents=True,exist_ok=True)

async def local():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            p=urlsplit(self.path);q=parse_qs(p.query);variant=q.get('variant',['one'])[0]
            body=f"<html><p>Test state {variant}</p><a href='/search?q=hello'>Search</a><a href='https://outside.invalid/'>Excluded</a></html>"
            if p.path=='/search':
                value=q.get('q',[''])[0];body='mysql_fetch error: SQL syntax MySQL' if "'" in value else 'Search '+value
            self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(body.encode())
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    cfg={**SETTINGS,'local_lab_origins':[origin],'request_interval':.05,'model_timeout':75}
    store=Store(DEST/('local-'+str(int(time.time()))+'.sqlite3'));engine=Engine(store,cfg)
    initial=await measure();engine.slots=capacity(initial,3)[0] or 1
    report={'kind':'controlled-fixture-real-models','model_health':await engine.models.health(),'initial_resources':initial,'runs':[]}
    spec={'profile':'lab','max_requests':14,'max_actions':12,'max_seconds':240,'force_retest':False,'continuous':False,'python_analysis':False}
    try:
        for label,url in [('first',origin+'/?variant=one'),('identical',origin+'/?variant=one'),('changed-data',origin+'/?variant=two')]:
            run=store.create(url,'127.0.0.1',spec);start=time.monotonic();print(label+' starting',flush=True)
            await engine.assess(run['id'],'benchmark-worker');result=store.detail(run['id'])
            item={'label':label,'seconds':round(time.monotonic()-start,2),'status':result['status'],'requests':result['requests'],'actions':len(result['actions']),'reused':sum(a['status']=='reused' for a in result['actions']),'candidates':len(result['findings']),'confirmed':sum(f['status']=='confirmed' for f in result['findings']),'model_errors':[e['message']+': '+str(e['data']) for e in result['events'] if e['kind']=='model_error'],'dispatches':sum(e['kind']=='dispatch' for e in result['events']),'detail':result}
            report['runs'].append(item);print(json.dumps({k:v for k,v in item.items() if k!='detail'}),flush=True)
        report['checks']={'identical_network_reduction':report['runs'][1]['requests']<report['runs'][0]['requests'],'changed_input_retested':report['runs'][2]['reused']==0,'no_false_confirmation':all(r['confirmed']==0 for r in report['runs']),'real_models_used':bool(engine.models.calls) and not any(r['model_errors'] for r in report['runs']),'parallel_dispatch_observed':any(r['dispatches'] for r in report['runs'])}
        report['model_calls']=engine.models.calls;report['final_resources']=await measure()
        (DEST/'local-benchmark.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(report['checks']),flush=True)
        if not all(report['checks'].values()):raise SystemExit(1)
    finally:server.shutdown();server.server_close();store.db.close()

async def public():
    targets=['https://ginandjuice.shop/','http://testphp.vulnweb.com/','http://testasp.vulnweb.com/','http://testaspnet.vulnweb.com/','http://testhtml5.vulnweb.com/']
    async with httpx.AsyncClient(timeout=15,trust_env=False) as client:
        session=(await client.get('http://127.0.0.1:7884/api/session')).json();headers={'X-Agent24-Token':session['token']};runs=[]
        for url in targets:
            r=await client.post('http://127.0.0.1:7884/api/runs',headers=headers,json={'url':url,'profile':'observe','max_requests':8,'max_actions':8,'max_seconds':180})
            if r.status_code!=200:runs.append({'url':url,'submission_error':r.text});continue
            run=r.json();runs.append({'url':url,'id':run['id']});print(url+' queued',flush=True)
        started=time.monotonic()
        while time.monotonic()-started<720:
            active=0
            for run in runs:
                if 'id' not in run:continue
                result=(await client.get('http://127.0.0.1:7884/api/runs/'+run['id'])).json();run['result']=result
                if result['status'] in ('queued','running','paused'):active+=1
            if not active:break
            await asyncio.sleep(3)
        report={'kind':'user-listed-public-practice-targets','profile':'bounded-read-only-observation','request_budget_per_run':8,'runs':runs,'elapsed_seconds':round(time.monotonic()-started,2)}
        (DEST/'public-benchmark.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        for run in runs:
            r=run.get('result',{});print(json.dumps({'url':run['url'],'status':r.get('status','submission_failed'),'requests':r.get('requests'), 'summary':r.get('summary',run.get('submission_error'))}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--public',action='store_true');args=parser.parse_args();asyncio.run(public() if args.public else local())
