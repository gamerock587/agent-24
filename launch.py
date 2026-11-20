"""Launch the local app and reuse existing model services. Own only processes started here."""
import json
import os
from pathlib import Path
import sys
import threading
import urllib.request
import webbrowser
from app.config import ROOT,DATA,SETTINGS

def main():
    os.chdir(ROOT);port=SETTINGS['port'];url=f'http://127.0.0.1:{port}'
    (DATA/'stop-requested').unlink(missing_ok=True)
    try:
        with urllib.request.urlopen(url+'/api/session',timeout=2) as response:
            if json.load(response).get('app')=='Agent 24':webbrowser.open(url);return
    except Exception:pass
    if not (ROOT/'.runtime/python-wasm/manifest.json').exists():
        print('Preparing the pinned Python/WASM analysis runtime...')
        try:
            from scripts.prepare_python import main as prepare_python
            prepare_python()
        except Exception as exc:print('Python sandbox preparation failed: '+str(exc)+'. Other tools remain available.')
    (DATA/'process.json').write_text(json.dumps({'pid':os.getpid(),'model_pid':None,'root':str(ROOT),'port':port}))
    from app.model_service import DecisionService
    decision_service=DecisionService(SETTINGS);decision_service.start()
    print('Agent 24: '+url+'\nQwen: '+SETTINGS['qwen_url']+'\nKeep LM Studio serving your Qwen model. Close this window to stop the app.')
    if '--no-browser' not in sys.argv:threading.Timer(2,lambda:webbrowser.open(url)).start()
    import uvicorn
    from app.api import create_app
    uvicorn.run(create_app(),host='127.0.0.1',port=port,log_level='warning')

if __name__=='__main__':main()

