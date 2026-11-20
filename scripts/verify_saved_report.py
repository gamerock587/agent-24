"""Verify one completed assessment's saved files and exported report, locally."""
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.request import urlopen
import zipfile

def main():
    ident=sys.argv[1]
    if not ident.isalnum():raise SystemExit('Invalid run id')
    base='http://127.0.0.1:7884/api/runs/'+ident
    def get(url):
        with urlopen(url,timeout=30) as response:return response.read()
    detail=json.loads(get(base))
    if detail['status'] in ('running','queued','paused'):raise SystemExit('Wait for assessment completion')
    manifest=json.loads(get(base+'/files'));folder=Path(manifest['folder'])
    checks={'saved_files_match_hashes':all(hashlib.sha256((folder/f['relative_path']).read_bytes()).hexdigest()==f['sha256'] for f in manifest['files'])}
    archive=zipfile.ZipFile(io.BytesIO(get(base+'/export/report')))
    names=archive.namelist()
    checks['zip_includes_report']=any(n.endswith('report.html') for n in names)
    checks['zip_includes_captures']=sum('/files/' in '/'+n for n in names)>=len(manifest['files'])
    sample=manifest['files'][-1]
    checks['download_matches_hash']=hashlib.sha256(get(base+'/files/'+sample['id'])).hexdigest()==sample['sha256']
    api=[a for a in detail['actions'] if a['tool']=='api_route_probe']
    counts={str(status):sum(a['result'].get('response',{}).get('status')==status for a in api) for status in (200,401,403,404)}
    result={'run':ident,'status':detail['status'],'requests':detail['requests'],'actions':len(detail['actions']),'files':len(manifest['files']),'historical_files':sum(f.get('observation')=='historical' for f in manifest['files']),'api_status_counts':counts,'findings':[{'title':f['title'],'status':f['status'],'endpoint':f['endpoint'],'evidence':f['evidence']} for f in detail['findings']],'model_errors':[e['message'] for e in detail['events'] if e['kind']=='model_error'],'analysis_hosts':[a['url'] for a in detail['actions'] if a['tool']=='evidence_analysis' and a['status']=='completed'],'checks':checks}
    output=Path(__file__).resolve().parents[1]/'.runtime/verification/salis-final-verification.json'
    output.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit('Report verification failed')

if __name__=='__main__':main()
