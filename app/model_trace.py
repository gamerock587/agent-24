"""Persist actual local model exchanges, without authentication headers."""
from contextlib import contextmanager
from contextvars import ContextVar
import re
import time
import json
from .store import uid,canonical

_context=ContextVar('agent24_model_context',default=None)

def trace_event(message,data=None):
    context=_context.get()
    if context:context[0].event(context[1],'code',message,redact(data or {}))

def redact(value):
    if isinstance(value,dict):return {k:('[redacted]' if re.search(r'authorization|api.?key|password|secret|access.?token|refresh.?token|set-cookie',str(k),re.I) else redact(v)) for k,v in value.items()}
    if isinstance(value,list):return [redact(v) for v in value]
    if isinstance(value,str):
        if value.lstrip().startswith(('{','[')):
            try:return canonical(redact(json.loads(value)))
            except (ValueError,TypeError):pass
        value=re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+',r'\1[redacted]',value)
        return re.sub(r'(?i)(["\']?(?:password|api_key|access_token|refresh_token|secret)["\']?\s*[:=]\s*["\'])[^"\']+',r'\1[redacted]',value)
    return value

@contextmanager
def trace_context(store,run_id,purpose):
    token=_context.set((store,run_id,purpose))
    try:yield
    finally:_context.reset(token)

async def traced_post(client,url,payload,model,headers=None):
    context=_context.get();ident=uid();started=time.time()
    if context:
        store,run_id,purpose=context
        store.execute('INSERT INTO model_turns VALUES(?,?,?,?,?,?,?,?,?)',(ident,run_id,model,purpose,'running',canonical(redact(payload)),'',started,0))
    try:
        response=await client.post(url,json=payload,**({'headers':headers} if headers else {}))
        if context:store.execute('UPDATE model_turns SET status=?,output=?,finished=? WHERE id=?',('completed' if response.status_code==200 else 'failed',canonical(redact({'http_status':response.status_code,'body':response.text[:200000]})),time.time(),ident))
        return response
    except BaseException as exc:
        if context:store.execute('UPDATE model_turns SET status=?,output=?,finished=? WHERE id=?',('failed',canonical({'error':type(exc).__name__}),time.time(),ident))
        raise
