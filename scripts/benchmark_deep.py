"""Exercise recursive discovery, two input parameters and memory with real models.

Uses the controlled HTTP fixture from the regression suite. Requires pytest
in the development environment; it never scans an external application.
"""
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import ROOT,SETTINGS,DATA
from app.engine import Engine
from app.store import Store
from app.resources import measure,capacity

async def main():
    module_spec=importlib.util.spec_from_file_location('deep_fixture',ROOT/'tests/test_deep_assessment.py')
    fixtures=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(fixtures)
    fixture=fixtures.site.__wrapped__();url,state=next(fixture)
    settings={**SETTINGS,'request_interval':.05,'request_timeout':3,'local_lab_origins':[url.rstrip('/')]}
    destination=DATA/'verification';destination.mkdir(exist_ok=True)
    store=Store(destination/f'deep-local-{int(time.time())}.sqlite3');engine=Engine(store,settings)
    engine.slots=capacity(await measure(),3)[0] or 1
    report={'kind':'recursive-controlled-fixture-real-models','health':await engine.models.health(),'runs':[]}
    try:
        for label in ('first','identical','changed-response'):
            if label=='changed-response':state['change']=True
            spec=fixtures.spec(include_subdomains=False,max_pages=40,crawl_depth=6,max_requests=100,max_actions=150,max_seconds=300)
            r=store.create(url,'127.0.0.1',spec);started=time.monotonic();print(label+' starting',flush=True)
            await engine.assess(r['id'],'deep-benchmark');detail=store.detail(r['id'])
            row={'label':label,'seconds':round(time.monotonic()-started,2),'requests':detail['requests'],'actions':len(detail['actions']),
                 'pages':detail['coverage']['pages_fetched'],'candidates':len(detail['findings']),
                 'reused':sum(a['status']=='reused' for a in detail['actions']),
                 'model_errors':[e for e in detail['events'] if e['kind']=='model_error'],'detail':detail}
            report['runs'].append(row);print(json.dumps({k:v for k,v in row.items() if k not in ('detail','model_errors')})+' model_errors='+str(len(row['model_errors'])),flush=True)
        first,second,third=report['runs']
        report['checks']={'recursive_surface':first['pages']>=12,'both_parameters_tested':len([a for a in first['detail']['actions'] if a['tool']=='database_error_probe'])==2,
                          'identical_probes_reused':all(a['status']=='reused' for a in second['detail']['actions'] if a['tool']=='database_error_probe'),
                          'changed_endpoint_retested':all(a['status']=='completed' for a in third['detail']['actions'] if a['tool']=='database_error_probe'),
                          'unrelated_endpoint_reused':any(a['status']=='reused' and a['url'].endswith('/hidden') for a in third['detail']['actions']),
                          'barrier_remains_visible':all(r['detail']['status']=='partial' and r['detail']['coverage']['stop_reason']=='access-or-availability-barriers' for r in report['runs']),
                          'no_false_confirmation':all(f['status']=='candidate' for r in report['runs'] for f in r['detail']['findings']),
                          'real_models_successful':bool(engine.models.calls) and all(not r['model_errors'] for r in report['runs'])}
        report['model_calls']=engine.models.calls
        (destination/'deep-local-benchmark.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(report['checks']),flush=True)
        if not all(report['checks'].values()):raise SystemExit(1)
    finally:
        fixture.close();store.db.close()

if __name__=='__main__':asyncio.run(main())
