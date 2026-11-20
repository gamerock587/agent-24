import asyncio
import json
import shutil
import psutil
import time

async def measure():
    ram=psutil.virtual_memory();gpu=None
    if shutil.which('nvidia-smi'):
        try:
            p=await asyncio.create_subprocess_exec('nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits',stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,creationflags=0x08000000 if __import__('os').name=='nt' else 0)
            raw,_=await asyncio.wait_for(p.communicate(),3)
            v=raw.decode().splitlines()[0].split(',')
            gpu={'name':v[0].strip(),'total_mb':int(v[1]),'used_mb':int(v[2]),'utilization':int(v[3]),'temperature':int(v[4])}
        except Exception:
            if 'p' in locals() and p.returncode is None:p.kill();await p.wait()
    return {'timestamp':time.time(),'ram_total_gb':round(ram.total/2**30,2),'ram_available_gb':round(ram.available/2**30,2),'ram_percent':ram.percent,'cpu_percent':psutil.cpu_percent(),'gpu':gpu}

def capacity(metrics,maximum=3):
    available=metrics.get('ram_available_gb',0)
    if available<1:return 0,'RAM reserve below 1 GB; workers wait.'
    slots=1
    if available>=4:slots=2
    if available>=8:slots=3
    gpu=metrics.get('gpu')
    if gpu and (gpu['temperature']>=83 or gpu['used_mb']/gpu['total_mb']>.97):
        slots=min(slots,1)
        reason='GPU pressure: one worker, serialized model calls.'
    else:reason='Independent tools overlap; model inference remains serialized.'
    return min(slots,maximum),reason

