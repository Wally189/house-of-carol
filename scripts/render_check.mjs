import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});

async function assertNoHorizontalOverflow(page,label){
  const g=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,bodyClient:document.body.clientWidth,bodyScroll:document.body.scrollWidth}));
  if(g.scroll>g.client+1||g.bodyScroll>g.bodyClient+1) throw new Error(`${label}: horizontal overflow ${JSON.stringify(g)}`);
}
async function assertFocus(page,label){
  await page.keyboard.press('Tab');
  const f=await page.evaluate(()=>{const el=document.activeElement;const s=getComputedStyle(el);const r=el.getBoundingClientRect();return{tag:el?.tagName||'',outline:s.outlineStyle,width:parseFloat(s.outlineWidth||'0'),visible:r.width>0&&r.height>0}});
  if(!f.visible||f.outline==='none'||f.width<1) throw new Error(`${label}: weak first focus ${JSON.stringify(f)}`);
}
async function exercise(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  const external=[];
  page.on('request',r=>{const u=new URL(r.url());if(u.hostname!=='127.0.0.1')external.push(r.url());});
  for(const [path,label] of [['index.html','home'],['ventures.html','ventures'],['about.html','about'],['how-we-work.html','how we work'],['contact.html','contact'],['privacy.html','privacy'],['terms.html','terms'],['404.html','404']]){
    await page.goto(`${BASE}/${path}`,{waitUntil:'networkidle'});
    await page.locator('h1').waitFor({state:'visible'});
    await assertNoHorizontalOverflow(page,`${name} ${label}`);
    if(path==='index.html'){
      const body=(await page.locator('body').innerText()).toLowerCase();
      for(const phrase of ['independent british venture business','intelligence','judgement','impact']) if(!body.includes(phrase)) throw new Error(`${name}: missing parent-brand signal ${phrase}`);
      if(await page.locator('a[href="ventures.html"]').count()===0) throw new Error(`${name}: ventures route missing`);
      for(const stale of ['workflow implementation','website release assurance','grand house','future-ready architecture','customer 000','engine architecture']) if(body.includes(stale)) throw new Error(`${name}: inward/stale/service-catalogue proposition present: ${stale}`);
      await assertFocus(page,`${name} home`);
      await page.screenshot({path:`qa-artifacts/${name}-home.png`,fullPage:true});
    }
  }
  await page.goto(`${BASE}/index.html`,{waitUntil:'networkidle'});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
  await assertNoHorizontalOverflow(page,`${name} 200% text`);
  if(external.length) throw new Error(`${name}: unexpected external requests ${[...new Set(external)].join(', ')}`);
  await context.close();
}
await exercise({width:1440,height:900},'desktop');
await exercise({width:390,height:844},'mobile');
await exercise({width:320,height:900},'reflow-320');
await exercise({width:800,height:1280},'tablet');
const noJsContext=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
const noJs=await noJsContext.newPage();
await noJs.goto(`${BASE}/index.html`,{waitUntil:'load'});
await noJs.locator('h1').waitFor({state:'visible'});
await assertNoHorizontalOverflow(noJs,'no-JS mobile');
await noJsContext.close();
await browser.close();
console.log('PASS: corporate House routes, responsive layouts, keyboard focus, enlarged-text and no-JS checks');
