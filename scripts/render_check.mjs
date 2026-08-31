import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const BUILD = 'customer-ready-20260831b';
const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});

async function assertNoHorizontalOverflow(page,label){
  const g=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,bodyClient:document.body.clientWidth,bodyScroll:document.body.scrollWidth}));
  if(g.scroll>g.client+1||g.bodyScroll>g.bodyClient+1){
    const offenders=await page.evaluate(()=>{
      const w=document.documentElement.clientWidth;
      return [...document.querySelectorAll('body *')].map(el=>{const r=el.getBoundingClientRect();return{tag:el.tagName,cls:el.className||'',id:el.id||'',left:Math.round(r.left),right:Math.round(r.right),width:Math.round(r.width),text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)}}).filter(x=>x.right>w+1||x.left<-1).slice(0,12);
    });
    throw new Error(`${label}: horizontal overflow ${JSON.stringify(g)} offenders=${JSON.stringify(offenders)}`);
  }
}
async function assertBuild(page,label){const b=await page.locator('meta[name="hoc-build"]').getAttribute('content');if(b!==BUILD)throw new Error(`${label}: wrong build ${b}`);}
async function assertFocus(page,label){
  await page.keyboard.press('Tab');
  const f=await page.evaluate(()=>{const el=document.activeElement;const s=getComputedStyle(el);const r=el.getBoundingClientRect();return{tag:el?.tagName||'',outline:s.outlineStyle,width:parseFloat(s.outlineWidth||'0'),visible:r.width>0&&r.height>0}});
  if(!f.visible||f.outline==='none'||f.width<2) throw new Error(`${label}: weak first focus ${JSON.stringify(f)}`);
}
async function exercise(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  const external=[];
  page.on('request',r=>{const u=new URL(r.url());if(u.hostname!=='127.0.0.1')external.push(r.url());});
  for(const [path,label] of [['index.html','home'],['catalogue.html','services'],['privacy.html','privacy'],['terms.html','terms'],['404.html','404']]){
    await page.goto(`${BASE}/${path}`,{waitUntil:'networkidle'});
    await assertBuild(page,`${name} ${label}`);
    await page.locator('h1').waitFor({state:'visible'});
    await assertNoHorizontalOverflow(page,`${name} ${label}`);
    if(path==='index.html'){
      for(const s of ['#work','#method','#contact']) if(!await page.locator(s).isVisible()) throw new Error(`${name}: missing ${s}`);
      const body=(await page.locator('body').innerText()).toLowerCase();
      for(const phrase of ['make the awkward part work','workflow implementation','website release assurance','two useful jobs']) if(!body.includes(phrase)) throw new Error(`${name}: missing ${phrase}`);
      for(const stale of ['data clean-up and structure','research for a decision','grand house','future-ready architecture']) if(body.includes(stale)) throw new Error(`${name}: stale public proposition present: ${stale}`);
      await assertFocus(page,`${name} home`);
      await page.screenshot({path:`qa-artifacts/${name}-home.png`,fullPage:true});
    }
  }
  await page.goto(`${BASE}/index.html`,{waitUntil:'networkidle'});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
  await assertNoHorizontalOverflow(page,`${name} 200% text`);
  if(!await page.locator('#work').isVisible()||!await page.locator('#contact').isVisible()) throw new Error(`${name}: core content lost at 200% text`);
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
await assertNoHorizontalOverflow(noJs,'no-JS mobile');
if(!await noJs.locator('#work').isVisible()||!await noJs.locator('#contact').isVisible()) throw new Error('no-JS: core customer content missing');
await noJsContext.close();
await browser.close();
console.log('PASS: customer-ready responsive, keyboard, enlarged-text, no-JS and locked-service checks');
