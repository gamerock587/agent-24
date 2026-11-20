"""Fetch the pinned official Pyodide core for network-disabled Python analysis."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.29.5'
FILES=['pyodide.js','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json']

def main():
    folder=ROOT/'.runtime/python-wasm';folder.mkdir(parents=True,exist_ok=True)
    def fetch(name):
        url=f'https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/{name}'
        with urllib.request.urlopen(url,timeout=60) as response:data=response.read(25_000_001)
        if len(data)>25_000_000:raise ValueError('Asset size limit')
        (folder/name).write_bytes(data)
        return {'file':name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,FILES))
    # Preserve the runtime's license alongside the downloaded dependency.
    license_url=f'https://raw.githubusercontent.com/pyodide/pyodide/{VERSION}/LICENSE'
    with urllib.request.urlopen(license_url,timeout=30) as response:(folder/'LICENSE').write_bytes(response.read())
    (folder/'manifest.json').write_text(json.dumps({'version':VERSION,'files':records,'source':'https://github.com/pyodide/pyodide','license_url':license_url},indent=2),encoding='utf8')
    print(json.dumps({'version':VERSION,'files':len(records),'bytes':sum(x['bytes'] for x in records)}))

if __name__=='__main__':main()
