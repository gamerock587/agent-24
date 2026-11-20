"""Python/WASM in a disposable browser worker, with request blocking and no host filesystem mount."""
import asyncio
from pathlib import Path
import os
from urllib.parse import urlsplit
from .config import ROOT

def browser_executable():
    # Prefer the installed browser rather than an unverified system command.
    cache=Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright'
    files=sorted(cache.glob('chromium-*/chrome-win64/chrome.exe'),reverse=True)
    return str(files[0]) if files else None

async def run_python(code,inputs,settings,timeout=20):
    if not (ROOT/'.runtime/python-wasm/manifest.json').exists():return {'status':'blocked','reason':'Python/WASM runtime is not prepared. Run scripts/prepare_python.py once.'}
    try:from playwright.async_api import async_playwright
    except ImportError:return {'status':'blocked','reason':'Playwright is required for the isolated Python worker.'}
    # Only one Playwright instance at a time — concurrent launches exhaust memory.
    import asyncio as _asyncio
    if not hasattr(run_python,'_lock'):run_python._lock=_asyncio.Lock()
    async with run_python._lock:
        return await _run_python_inner(code,inputs,settings,timeout)

async def _run_python_inner(code,inputs,settings,timeout=20):
    from playwright.async_api import async_playwright
    root=f'http://127.0.0.1:{settings["port"]}';locked=False;blocked=[]
    async with async_playwright() as playwright:
        executable=browser_executable()
        browser=await playwright.chromium.launch(headless=True,args=['--js-flags=--max-old-space-size=128 --wasm-max-mem-pages=4096'],**({'executable_path':executable} if executable else {}))
        context=await browser.new_context(service_workers='block',accept_downloads=False)
        async def route(request_route):
            value=request_route.request.url
            parsed=urlsplit(value);base=urlsplit(root)
            allowed=not locked and (parsed.scheme,parsed.netloc)==(base.scheme,base.netloc) and (parsed.path.startswith('/python-runtime/') or parsed.path in ('/sandbox','/static/python-worker.js','/static/python-host.js'))
            if allowed:await request_route.continue_()
            else:blocked.append(value[:300]);await request_route.abort()
        await context.route('**/*',route)
        async def block_socket(socket):
            blocked.append(socket.url[:300]);await socket.close()
        await context.route_web_socket('**/*',block_socket)
        page=await context.new_page()
        try:
            await page.goto(root+'/sandbox',timeout=15000)
            await page.wait_for_function('()=>window.pythonReady || window.pythonError',timeout=15000)
            error=await page.evaluate('window.pythonError')
            if error:return {'status':'failed','reason':error,'sandbox':'python-wasm'}
            locked=True
            await page.evaluate('(args)=>window.pythonWorker.postMessage(args)',{'code':code,'inputs':inputs})
            try:await page.wait_for_function('()=>window.pythonResult !== null',timeout=timeout*1000)
            except Exception:
                await page.evaluate('window.pythonWorker.terminate()')
                return {'status':'failed','reason':'Python execution time budget exceeded. Worker terminated.','sandbox':'python-wasm','network_blocked':blocked}
            result=await page.evaluate('window.pythonResult')
            return {**result,'sandbox':'python-wasm','network_blocked':blocked,'host_filesystem_access':False}
        finally:
            await context.close();await browser.close()
