"""Exercise the local UI, capture desktop/mobile images and record observed errors."""
from pathlib import Path
import asyncio
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.async_api import async_playwright
from app.python_sandbox import browser_executable
from app.config import DATA

async def main():
    folder=DATA/'verification';folder.mkdir(parents=True,exist_ok=True);errors=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=browser_executable())
        page=await browser.new_page(viewport={'width':1560,'height':1040},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('console',lambda message:errors.append(message.text) if message.type=='error' else None)
        await page.goto('http://127.0.0.1:7884',wait_until='networkidle');await page.wait_for_timeout(1500)
        response=await page.request.get('http://127.0.0.1:7884/api/state')
        runs=(await response.json())['runs']
        populated=next((r for r in runs if r['domain']=='ginandjuice.shop' and r['status']=='completed'),None)
        if populated:
            await page.evaluate('(id)=>selectRun(id)',populated['id'])
            await page.wait_for_timeout(400)
        await page.screenshot(path=str(folder/'ui-desktop.png'),full_page=True)
        await page.get_by_role('button',name='Domain history').click();await page.wait_for_timeout(300)
        history_count=await page.locator('.history-domain').count()
        await page.get_by_role('button',name='Close history').click()
        await page.get_by_role('button',name='Skills & tools').click()
        await page.get_by_role('textbox',name='Search skills').fill('SSRF');await page.wait_for_timeout(800)
        skill_matches=await page.locator('.skill-card').count();assert skill_matches>0
        await page.get_by_role('button',name='Practice labs').click();await page.wait_for_timeout(700)
        scenario_count=await page.locator('#scenario-list .skill-card').count();assert scenario_count==162
        await page.get_by_role('button',name='Test memory').click();await page.wait_for_timeout(500)
        await page.get_by_role('button',name='Workspace',exact=False).click();await page.wait_for_timeout(300)
        artifact=page.locator('.evidence-row').first
        if await artifact.count():await artifact.click();await page.wait_for_timeout(400);assert await page.locator('#inspection pre').count()
        desktop_overflow=await page.evaluate('document.documentElement.scrollWidth>innerWidth')
        await page.set_viewport_size({'width':390,'height':844});await page.wait_for_timeout(500)
        mobile_overflow=await page.evaluate('document.documentElement.scrollWidth>innerWidth')
        await page.screenshot(path=str(folder/'ui-mobile.png'),full_page=True)
        await browser.close()
    report={'history_domains':history_count,'skill_search_cards':skill_matches,'scenario_cards':scenario_count,'desktop_horizontal_overflow':desktop_overflow,'mobile_horizontal_overflow':mobile_overflow,'browser_errors':errors}
    (folder/'ui-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
    if errors or desktop_overflow or mobile_overflow:raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
