"""Watch the decision service; own only models started by Agent 24."""
import atexit
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import urllib.request
from urllib.parse import urlsplit
import psutil
from .config import ROOT,DATA

class DecisionService:
    def __init__(self,settings):
        self.s=settings;self.process=None;self.log=None;self.closed=threading.Event();self.starts=0
    def ready(self):
        key=Path(self.s['key_file'])
        if not key.is_absolute():key=ROOT/key
        headers={'Authorization':'Bearer '+key.read_text().strip()} if key.exists() else {}
        try:
            with urllib.request.urlopen(urllib.request.Request(self.s['d1_url']+'/health',headers=headers),timeout=2) as r:return r.status==200
        except Exception:return False
    def occupied(self):
        p=urlsplit(self.s['d1_url'])
        with socket.socket() as sock:
            sock.settimeout(1);return sock.connect_ex((p.hostname,p.port or 8081))==0
    def start_model(self):
        if self.ready() or self.occupied():return
        if self.process and self.process.poll() is None:return
        if psutil.virtual_memory().available<4*2**30:
            print('d1 watchdog: waiting for at least 4 GB available RAM.',flush=True);return
        exe=Path(self.s.get('llama_path', str(ROOT/'runtime/llama/llama-server.exe')));model=Path(self.s.get('model_path', str(ROOT/'models/d1-3B-Q4_K_M.gguf')));projector=Path(self.s.get('projector_path', str(ROOT/'models/mmproj-d1-3B-Q8_0.gguf')));key=Path(self.s['key_file'])
        exe=exe if exe.is_absolute() else ROOT/exe
        model=model if model.is_absolute() else ROOT/model
        projector=projector if projector.is_absolute() else ROOT/projector
        if not key.is_absolute():key=ROOT/key
        if not all(p.exists() for p in (exe,model,key)):
            print('d1 watchdog: configured runtime, model or existing key is missing.',flush=True);return
        gpu_free=0
        try:
            info=subprocess.run(['nvidia-smi','--query-gpu=memory.total,memory.used','--format=csv,noheader,nounits'],capture_output=True,timeout=3,creationflags=subprocess.CREATE_NO_WINDOW)
            total,used=map(int,info.stdout.decode().splitlines()[0].split(','));gpu_free=total-used
        except Exception:pass
        mode='GPU' if gpu_free>=3072 else 'CPU'
        if self.log:self.log.close()
        self.log=(DATA/'d1.log').open('a',encoding='utf8')
        p=urlsplit(self.s['d1_url'])
        args=[str(exe),'-m',str(model),'--host',p.hostname,'--port',str(p.port or 8081),'-ngl','all' if mode=='GPU' else '0','-c','4096','-np','1','-t','4','--api-key-file',str(key),'--no-webui']
        if projector.exists():
            args+=['--mmproj',str(projector)]
            if mode=='CPU':args+=['--no-mmproj-offload']
        self.process=subprocess.Popen(args,cwd=exe.parent,stdout=self.log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        self.starts+=1
        (DATA/'process.json').write_text(json.dumps({'pid':os.getpid(),'model_pid':self.process.pid,'root':str(ROOT),'port':self.s['port'],'d1_mode':mode}))
        print(f'd1 watchdog: started owned {mode} service; GPU headroom {gpu_free} MB.',flush=True)
    def loop(self):
        while not self.closed.wait(10):
            if not self.ready():
                if self.starts>=4:
                    print('d1 watchdog: restart circuit breaker reached; inspect .runtime/d1.log.',flush=True);self.closed.wait(60);continue
                self.start_model()
    def start(self):
        self.start_model();threading.Thread(target=self.loop,daemon=True).start();atexit.register(self.close)
    def close(self):
        self.closed.set()
        if self.process and self.process.poll() is None:self.process.terminate()
        if self.log:self.log.close()
