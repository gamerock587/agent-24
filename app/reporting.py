"""Visible, local assessment files and human-readable reports."""
import csv
import hashlib
import html
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from .config import ROOT,DATA

def folder(run,store=None):
    domain=re.sub(r'[^a-zA-Z0-9.-]','_',run['domain'])
    ident=re.sub(r'[^a-zA-Z0-9_-]','_',run['id'])
    report_root=ROOT/'Reports'
    if store is not None:
        database=Path(store.db.execute('PRAGMA database_list').fetchone()[2]).resolve()
        if database!=(DATA/'agent24.sqlite3').resolve():report_root=DATA/'verification'/'reports'
    value=report_root/domain/ident;value.mkdir(parents=True,exist_ok=True);return value

def capture(store,run,artifact,result):
    response=result.get('response')
    if not response:return
    base=folder(run,store);p=urlsplit(response['url']);mime=response['headers'].get('content-type','').split(';')[0]
    name=Path(p.path).name or 'index';name=re.sub(r'[^a-zA-Z0-9._-]','_',name)[:90]
    extension={ 'text/html':'.html','application/json':'.json','application/javascript':'.js','text/javascript':'.js','application/xml':'.xml','text/xml':'.xml'}.get(mime,'.txt')
    if '.' not in name:name+=extension
    name=Path(name).stem+'-'+artifact+Path(name).suffix
    if mime in ('text/html','application/xhtml+xml'):name+='.txt'
    host=re.sub(r'[^a-zA-Z0-9.-]','_',p.hostname or run['domain'])
    relative='files/'+host+'/'+name;raw=response['body'].encode('utf8')
    destination=base/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
    store.execute('INSERT OR REPLACE INTO captured_files VALUES(?,?,?,?,?,?,?,?,?,?)',(artifact,run['id'],response['url'],response['status'],mime,len(raw),hashlib.sha256(raw).hexdigest(),int(response.get('truncated',False)),relative,result.get('tested_url',response['url'])))

def files(store,ident):
    return store.rows("SELECT f.*,CASE WHEN a.name='historical-response.json' THEN 'historical' ELSE 'current-run' END observation,a.created saved_at FROM captured_files f LEFT JOIN artifacts a ON a.id=f.id WHERE f.run_id=? ORDER BY f.rowid",(ident,))

def write_report(store,ident):
    run=store.detail(ident);base=folder(run,store);captured=files(store,ident);coverage=run.get('coverage') or {}
    def write(name,value):(base/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
    write('report.json',run);write('hosts.json',coverage.get('discovered_hosts',[]));write('endpoints.json',coverage.get('endpoints',[]));write('findings.json',run['findings']);write('files.json',captured)
    for name,rows,columns in [('endpoints.csv',coverage.get('endpoints',[]),['url','status','http_status','final_url','source','parent','depth']),('files.csv',captured,['tested_url','url','status','mime','bytes','sha256','truncated','relative_path','id','observation','saved_at'])]:
        with (base/name).open('w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    analyses=[{'tool':a['tool'],'url':a['url'],'status':a['status'],'result':a['result']} for a in run['actions'] if a['status']!='superseded' and a['tool'] in ('javascript_review','evidence_analysis','tls_certificate_review','file_exposure_probe','api_inventory','api_route_probe')]
    write('analysis.json',analyses)
    lines=['# Agent 24 assessment',f'Target: {run["url"]}',f'Run: {ident}',f'Status: {run["status"]}',run['summary'],'','## Observed findings']
    for finding in run['findings']:lines.extend([f'### {finding["title"]}',f'{finding["status"]} · {finding["severity"]}',finding['endpoint'],finding['detail'],f'Evidence: {finding["evidence"]}'])
    if not run['findings']:lines.append('No findings were established by the executed checks.')
    lines+=['','## Coverage',f'Captured responses: {len(captured)}',f'Unvisited crawl leads: {coverage.get("frontier_remaining",0)}',f'Stop reason: {coverage.get("stop_reason") or "enabled workflow finished"}',
            'Read analysis.json for source observations and evidence-linked model analysis. files.csv maps every saved file back to its request, status, SHA-256 and truncation flag.',
            'Response files include error pages. A filename or HTTP 200 alone is not proof of sensitive-file exposure. Findings distinguish confirmed configuration failures from candidates requiring impact validation.']
    (base/'report.md').write_text('\n\n'.join(lines),encoding='utf8')
    escape=lambda value:html.escape(str(value))
    finding_html=''.join(f'<article><h3>{escape(f["title"])}</h3><b>{escape(f["status"])} · {escape(f["severity"])}</b><p>{escape(f["endpoint"])}</p><p>{escape(f["detail"])}</p></article>' for f in run['findings']) or '<p>No findings established by executed checks.</p>'
    file_html=''.join(f'<tr><td>{escape(f["url"])}</td><td>{f["status"]}</td><td>{escape(f["mime"])}</td><td>{f["bytes"]}</td><td><a href="{escape(f["relative_path"])}">Saved response</a>{" (truncated)" if f["truncated"] else ""}</td></tr>' for f in captured)
    document=f'''<!doctype html><meta charset="utf-8"><title>Agent 24 · {escape(run['domain'])}</title><meta name="viewport" content="width=device-width"><style>body{{font:15px/1.6 system-ui;margin:40px auto;padding:0 24px;max-width:1150px;color:#252338;background:#faf9fe}}h1,h2{{color:#7137df}}article{{padding:18px;background:white;border:1px solid #e8defa;border-radius:12px;margin:15px 0}}table{{border-collapse:collapse;width:100%;background:white;font-size:12px}}td,th{{text-align:left;padding:9px;border:1px solid #e7e4ef;overflow-wrap:anywhere}}a{{color:#7137df}}code{{overflow-wrap:anywhere}}</style><h1>Agent 24 · {escape(run['domain'])}</h1><p>{escape(run['summary'])}</p><p>Run <code>{escape(ident)}</code> · {escape(run['status'])}</p><p><a href="analysis.json">Analysis</a> · <a href="endpoints.csv">Endpoints CSV</a> · <a href="files.csv">Files CSV</a> · <a href="report.json">Full report</a></p><h2>Findings</h2>{finding_html}<h2>Collected response files ({len(captured)})</h2><p>These are response captures, including errors; consult HTTP status and findings before interpreting exposure.</p><table><tr><th>Request URL</th><th>HTTP</th><th>Type</th><th>Bytes</th><th>File</th></tr>{file_html}</table>'''
    (base/'report.html').write_text(document,encoding='utf8')
    history=[]
    for report in base.parent.glob('*/report.json'):
        try:
            previous=json.loads(report.read_text(encoding='utf8'))
            history.append((previous['created'],f'<article><h2><a href="{escape(report.parent.name)}/report.html">{escape(previous["id"])}</a></h2><p>{escape(previous["status"])} · {escape(previous["summary"])}</p></article>'))
        except (ValueError,KeyError):continue
    index='<!doctype html><meta charset="utf-8"><title>Agent 24 reports</title><style>body{font:15px/1.6 system-ui;max-width:950px;margin:40px auto;padding:20px;background:#faf9fe;color:#252338}article{background:white;border:1px solid #e6dcf7;padding:20px;margin:15px 0;border-radius:12px}a{color:#7137df}</style><h1>'+escape(run['domain'])+' · Assessment history</h1>'+''.join(row for _,row in sorted(history,reverse=True))
    (base.parent/'index.html').write_text(index,encoding='utf8')
    return {'folder':str(base),'report':str(base/'report.html'),'files':len(captured)}
