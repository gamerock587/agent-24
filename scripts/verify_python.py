from pathlib import Path
import asyncio
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.python_sandbox import run_python
from app.models import Models
from app.tools import execute
from app.config import SETTINGS,DATA

async def main():
    inputs={'values':[1,2,3]}
    normal=await run_python('import json\ndata=json.load(open("/work/input.json"))\nprint(json.dumps({"sum":sum(data["values"])}))',inputs,SETTINGS)
    network=await run_python('from js import fetch\nawait fetch("http://127.0.0.1:7884/api/session")',inputs,SETTINGS)
    timeout=await run_python('while True: pass',inputs,SETTINGS,timeout=2)
    memory=await run_python('try:\n    a=bytearray(400*1024*1024)\n    print("UNEXPECTED_ALLOCATION")\nexcept MemoryError:\n    print("MEMORY_LIMIT_ENFORCED")',inputs,SETTINGS)
    baseline={'status':200,'headers':{'content-type':'text/html'},'body':'<html><a href="/demo">Demo</a></html>','url':'https://example.com/'}
    generated=await execute({'tool':'python_analysis'}, {'id':'python-verification','url':'https://example.com/'},baseline,None,Models(SETTINGS),SETTINGS)
    report={'normal':normal,'network_attempt':network,'timeout':timeout,'memory_limit':memory,'qwen_generated_analysis':generated,'checks':{'python_executed':normal.get('status')=='completed' and '6' in normal.get('stdout',''),'network_blocked':bool(network.get('network_blocked')) and network.get('status')=='failed','infinite_loop_terminated':'time budget' in timeout.get('reason',''),'wasm_memory_limit':memory.get('stdout')=='MEMORY_LIMIT_ENFORCED','generated_code_executed':generated.get('status')=='completed'}}
    folder=DATA/'verification';folder.mkdir(parents=True,exist_ok=True);(folder/'python-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
    if not all(report['checks'].values()):raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
