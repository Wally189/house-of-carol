import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});

async function assertNoOverflow(page,label){
  const g=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,bodyClient:document.body.clientWidth,bodyScroll:document.body.scrollWidth}));
  if(g.scroll>g.client+1||g.bodyScroll>g.bodyClient+1) throw new Error(`${label}: horizontal overflow ${JSON.stringify(g)}`);
}

async function assertContent(page,label){
  const body=(await page.locator('body').innerText()).toLowerCase();
  const required=['we build useful businesses.','what we build','how we work','our businesses and ventures','bristol, united kingdom'];
  for(const phrase of required) if(!body.includes(phrase)) throw new Error(`${label}: missing ${phrase}`);
  const forbidden=['grand house','fields','threshold','workflow implementation','website release assurance','coming soon','current ventures','ai-powered','contact us'];
  for(const phrase of forbidden) if(body.includes(phrase)) throw new Error(`${label}: stale/forbidden material ${phrase}`);
  const counts=await page.evaluate(()=>({sections:document.querySelectorAll('main > section').length,navs:document.querySelectorAll('nav').length,forms:document.querySelectorAll('form').length,scripts:document.querySelectorAll('script').length,links:[...document.querySelectorAll('a')].map(a=>a.getAttribute('href'))}));
  if(counts.sections!==4) throw new Error(`${label}: expected four public sections, got ${counts.sections}`);
  if(counts.navs||counts.forms||counts.scripts) throw new Error(`${label}: unauthorised navigation/form/script present ${JSON.stringify(counts)}`);
  const nonTechnical=counts.links.filter(h=>h && h!=='#main' && h!=='index.html');
  if(nonTechnical.length) throw new Error(`${label}: unexpected link(s) ${nonTechnical.join(', ')}`);
}

async function run(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  const external=[];
  page.on('request',r=>{const u=new URL(r.url());if(u.hostname!=='127.0.0.1')external.push(r.url());});
  await page.goto(`${BASE}/index.html`,{waitUntil:'networkidle'});
  await page.locator('h1').waitFor({state:'visible'});
  await assertContent(page,name);
  await assertNoOverflow(page,name);
  await page.keyboard.press('Tab');
  const firstFocus=await page.evaluate(()=>{const el=document.activeElement;const s=getComputedStyle(el);return{tag:el?.tagName||'',outline:s.outlineStyle,width:parseFloat(s.outlineWidth||'0')}});
  if(firstFocus.tag!=='A'||firstFocus.outline==='none'||firstFocus.width<1) throw new Error(`${name}: skip-link focus not visible ${JSON.stringify(firstFocus)}`);
  await page.screenshot({path:`qa-artifacts/${name}-home.png`,fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
  await assertNoOverflow(page,`${name} 200% text`);
  if(external.length) throw new Error(`${name}: unexpected external requests ${[...new Set(external)].join(', ')}`);
  await context.close();
}

await run({width:1440,height:900},'desktop');
await run({width:800,height:1280},'tablet');
await run({width:390,height:844},'mobile');
await run({width:320,height:900},'reflow-320');

const noJsContext=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
const noJs=await noJsContext.newPage();
await noJs.goto(`${BASE}/index.html`,{waitUntil:'load'});
await noJs.locator('h1').waitFor({state:'visible'});
await assertContent(noJs,'no-JS mobile');
await assertNoOverflow(noJs,'no-JS mobile');
await noJsContext.close();

await browser.close();
console.log('PASS: restrained parent-company site across desktop/tablet/mobile/reflow, exact content envelope, no-JS and keyboard focus');
