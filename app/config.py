from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('AGENT24_DATA', ROOT / '.runtime')).resolve()
DATA.mkdir(parents=True, exist_ok=True)
DEFAULTS = {'port':7884,'qwen_url':'http://localhost:1235/v1','qwen_model':'qwen/qwen3.5-9b','qwen_adapter':'lmstudio',
    'd1_url':'http://127.0.0.1:8081','key_file':str(ROOT.parent/'runtime/local-api-key.txt'),
    'max_workers':3,'model_timeout':75,'request_interval':1.0,'request_timeout':12,
    'memory_ttl_hours':24,'recurrence_seconds':900,'max_requests':120,'max_actions':180,
    'local_lab_origins':[],'docker_image':'python:3.12-slim'}
CONFIG_PATH = ROOT/'config/settings.json'
SETTINGS = {**DEFAULTS, **(json.loads(CONFIG_PATH.read_text(encoding='utf8')) if CONFIG_PATH.exists() else {})}

