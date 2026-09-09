import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const EXPECTED_NAV=['index.html','how-it-works.html','catalogue.html','about.html','contact.html'];

async function noOverflow(page,label){
  const g=await page.evaluate(()=>{
    const w=document.documentElement.clientWidth;
    const offenders=[...document.querySelectorAll('*')].map(el=>{const r=el.getBoundingClientRect();return {tag:el.tagName,left:r.left,right:r.right,text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)}}).filter(x=>x.right>w+1||x.left<-1).slice(0,10);
    return {w,offenders};
  });
  if(g.offenders.length) throw new Error(label+': visible overflow '+JSON.stringify(g));
}

async function baseline(page,path,label){
  const response=await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});
  if(!response||!response.ok()) throw new Error(label+': HTTP '+response?.status());
  if(await page.locator('h1').count()!==1) throw new Error(label+': H1 count');
  const nav=await page.locator('.main-nav a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
  if(JSON.stringify(nav)!==JSON.stringify(EXPECTED_NAV)) throw new Error(label+': nav '+JSON.stringify(nav));
  await noOverflow(page,label);
}

async function run(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();

  await baseline(page,'catalogue.html',name+' catalogue');
  if((await page.locator('.service-entry h3 a').count())!==52) throw new Error(name+': catalogue service link count');
  if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+': catalogue displays a price');
  const reps=await page.locator('.service-family').evaluateAll(families=>families.map(f=>f.querySelector('.service-entry h3 a')?.getAttribute('href')).filter(Boolean));
  if(reps.length!==7) throw new Error(name+': representative family links '+JSON.stringify(reps));
  await page.screenshot({path:'qa-artifacts/'+name+'-catalogue.png',fullPage:true});
  await page.evaluate(()=>{document.body.style.fontSize='200%'});
  await noOverflow(page,name+' catalogue 200%');

  for(const href of reps){
    await baseline(page,href,name+' '+href);
    const body=(await page.locator('body').innerText()).toLowerCase();
    if(!body.includes('pricing') && !/£\s?\d/.test(body)) throw new Error(name+' '+href+': pricing information missing');
    await page.evaluate(()=>{document.body.style.fontSize='200%'});
    await noOverflow(page,name+' '+href+' 200%');
  }

  await baseline(page,'contact.html',name+' contact');
  if(await page.locator('form').count()!==1) throw new Error(name+': contact form count');
  await context.close();
}

for(const [v,n] of [[{width:1440,height:900},'desktop'],[{width:800,height:1280},'tablet'],[{width:390,height:844},'mobile'],[{width:320,height:900},'reflow-320']]) await run(v,n);
await browser.close();
console.log('PASS: catalogue directory and representative service-detail pages render across desktop, tablet, mobile, 320px reflow and 200% text');
