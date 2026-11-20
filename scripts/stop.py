"""Stop only the verified Agent 24 process and its specifically recorded model child."""
from pathlib import Path
import json
import sys
import psutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import ROOT,DATA

def main():
    path=DATA/'process.json'
    if not path.exists():print('No Agent 24 process record.');return
    record=json.loads(path.read_text(encoding='utf8'))
    if Path(record['root']).resolve()!=ROOT:raise SystemExit('Process record belongs to another directory.')
    try:process=psutil.Process(record['pid'])
    except psutil.NoSuchProcess:print('Agent 24 is already stopped.');return
    if Path(process.cwd()).resolve()!=ROOT or not any(Path(a).name=='launch.py' for a in process.cmdline()):raise SystemExit('Process identity mismatch; nothing was stopped.')
    (DATA/'stop-requested').write_text('User explicitly stopped Agent 24.',encoding='utf8')
    model_pid=record.get('model_pid')
    if model_pid:
        try:
            model=psutil.Process(model_pid)
            if model.ppid()==process.pid and model.name().lower()=='llama-server.exe':model.terminate()
        except psutil.NoSuchProcess:pass
    process.terminate();print('Agent 24 stopped. Existing LM Studio and reused model services were preserved.')

if __name__=='__main__':main()
