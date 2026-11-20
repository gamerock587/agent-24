"""Rebuild bounded model priorities from saved evidence, without target requests."""
import asyncio
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import SETTINGS
from app.engine import Engine
from app.store import Store
from app.reporting import write_report

class NoNetwork:
    async def fetch(self,*args,**kwargs):raise RuntimeError('This operation only reads saved evidence')

async def main():
    db=Store();ident=sys.argv[1];detail=db.detail(ident)
    if detail['status'] in ('running','queued','paused'):raise SystemExit('Wait for assessment completion')
    engine=Engine(db,SETTINGS,network=NoNetwork());run=db.run(ident);run['_deadline']=time.monotonic()+600
    observations={};responses={}
    for a in db.rows('SELECT id,path FROM artifacts WHERE run_id=? ORDER BY created',(ident,)):
        try:value=json.loads(Path(a['path']).read_text(encoding='utf8'))
        except (ValueError,OSError):continue
        response=value.get('response')
        if response and response.get('status')==200:
            response['_evidence_id']=a['id'];responses[response['url']]=response
    for a in detail['actions']:
        if a['tool'] not in ('javascript_review','api_inventory','api_route_probe','tls_certificate_review','file_exposure_probe'):continue
        result=a['result'];observed={k:v for k,v in result.items() if k not in ('response','tested_url')}
        if result.get('response'):observed['http_status']=result['response']['status'];observed['response_url']=result['response']['url']
        observations.setdefault(urlsplit(a['url']).hostname,[]).append({'url':a['url'],'observation':observed,'evidence_id':result.get('evidence_id')})
    db.event(ident,'analysis-quality','Replacing unconstrained model commentary with recorded facts and validated follow-up choices. Original evidence remains retained.',{})
    results=[]
    for host in sorted({urlsplit(u).hostname for u in responses}):
        sample=max((r for u,r in responses.items() if urlsplit(u).hostname==host),key=lambda r:('application/json' in r['headers'].get('content-type',''),bool(re.search(r'jQuery\s+v?1\.12\.4',r['body'][:1200])),any(x in r['body'] for x in ('baseURL','baseUrl'))))
        obs=observations.get(host,[])
        obs.sort(key=lambda x:(bool(x['observation'].get('findings')),bool(x['observation'].get('mapped_get_urls')),x['observation'].get('http_status')==200),reverse=True)
        routes=[{'url':p['url'],'status':p.get('http_status'),'state':p['status'],'final_url':p.get('final_url')} for p in detail.get('coverage',{}).get('endpoints',[]) if urlsplit(p['url']).hostname==host]
        data={'observations':obs[:12],'routes':routes,'evidence_ids':[sample['_evidence_id']]+[o['evidence_id'] for o in obs[:12] if o.get('evidence_id')]}
        result=await engine.action(run,'analysis-revision',{'tool':'evidence_analysis','url':sample['url'],'data':data},sample)
        if not result.get('model_selection_valid'):raise RuntimeError('Model returned an invalid recommendation selection')
        for a in detail['actions']:
            if a['tool']=='evidence_analysis' and urlsplit(a['url']).hostname==host:db.execute('UPDATE actions SET status=? WHERE id=?',('superseded',a['id']))
        db.event(ident,'analysis',f'Validated evidence analysis saved for {host}.',{'evidence_id':result['evidence_id'],'network_requests':0})
        results.append({'host':host,'valid':True,'evidence':result['evidence_id']});print(json.dumps(results[-1]),flush=True)
    current=db.detail(ident);confirmed=sum(f['status']=='confirmed' for f in current['findings'])
    summary=re.sub(r'\d+ candidates\.',f'{confirmed} confirmed findings, {len(current["findings"])-confirmed} candidates.',current['summary'])
    summary=re.sub(r'\d+ actions,',str(len(current['actions']))+' actions,',summary)
    db.update(ident,summary=summary)
    write_report(db,ident);db.event(ident,'report','Saved corrected evidence analysis and refreshed Reports files.',{'hosts':len(results),'new_target_requests':0})
    db.db.close()

if __name__=='__main__':asyncio.run(main())
