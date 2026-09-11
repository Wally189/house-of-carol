import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const EXPECTED_NAV=['index.html','how-it-works.html','catalogue.html','about.html','contact.html'];
const AREA_PAGES=["catalogue-operations.html","catalogue-ai-digital.html","catalogue-commercial.html","catalogue-learning.html","catalogue-research.html","catalogue-charity-public.html","catalogue-church-parish.html"];
const AREA_LINKS='.area-entry .area-card-link';
const SERVICE_LINKS='.service-entry .service-card-link';

async function noOverflow(page,label){
  const g=await page.evaluate(()=>{
    const w=document.documentElement.clientWidth;
    const offenders=[...document.querySelectorAll('*')].map(el=>{const r=el.getBoundingClientRect();return {tag:el.tagName,left:r.left,right:r.right,text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)}}).filter(x=>x.right>w+1||x.left<-1).slice(0,10);
    return {w,offenders};
  });
  if(g.offenders.length) throw new Error(label+': visible overflow '+JSON.stringify(g));
}

async function noStickyInset(locator,label){
  const shadow=await locator.evaluate(el=>getComputedStyle(el).boxShadow);
  if(shadow!=='none') throw new Error(label+': touch navigation left an inset/hover shadow '+shadow);
}

async function baseline(page,path,label){
  const response=await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});
  if(!response||!response.ok()) throw new Error(label+': HTTP '+response?.status());
  if(await page.locator('h1').count()!==1) throw new Error(label+': H1 count');
  const nav=await page.locator('.main-nav a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
  if(JSON.stringify(nav)!==JSON.stringify(EXPECTED_NAV)) throw new Error(label+': nav '+JSON.stringify(nav));
  await noOverflow(page,label);
}

async function tapAllAndReturn(page,selector,label){
  const count=await page.locator(selector).count();
  for(let i=0;i<count;i++){
    const link=page.locator(selector).nth(i);
    const href=await link.getAttribute('href');
    if(!href) throw new Error(label+': missing href at '+i);
    const expected=new URL(href,page.url()).href;
    await Promise.all([page.waitForURL(expected),link.tap()]);
    if(page.url()!==expected) throw new Error(label+': tap did not navigate to '+href);
    await page.goBack({waitUntil:'networkidle'});
    await noStickyInset(page.locator(selector).nth(i),label+' return '+href);
  }
}

async function run(viewport,name){
  const context=await browser.newContext({viewport,hasTouch:name==='mobile'||name==='reflow-320'});
  const page=await context.newPage();

  await baseline(page,'catalogue.html',name+' catalogue');
  if((await page.locator(AREA_LINKS).count())!==7) throw new Error(name+': main catalogue area count');
  if((await page.locator('.service-entry').count())!==0) throw new Error(name+': main catalogue exposes service entries');
  if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+': main catalogue displays a price');
  if(name==='mobile') await tapAllAndReturn(page,AREA_LINKS,name+' main catalogue');
  await page.screenshot({path:'qa-artifacts/'+name+'-catalogue.png',fullPage:true});
  await page.evaluate(()=>{document.body.style.fontSize='200%'});
  await noOverflow(page,name+' catalogue 200%');

  const products=[];
  const reps=[];
  for(const area of AREA_PAGES){
    await baseline(page,area,name+' '+area);
    const serviceCount=await page.locator(SERVICE_LINKS).count();
    if(serviceCount<1) throw new Error(name+' '+area+': no service links');
    if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+' '+area+': area displays a price');
    const hrefs=await page.locator(SERVICE_LINKS).evaluateAll(a=>a.map(x=>x.getAttribute('href')));
    products.push(...hrefs);
    reps.push(hrefs[0]);
    if(name==='mobile') await tapAllAndReturn(page,SERVICE_LINKS,name+' '+area);
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-'+area.replace('.html','')+'.png',fullPage:true});
    await page.evaluate(()=>{document.body.style.fontSize='200%'});
    await noOverflow(page,name+' '+area+' 200%');
  }

  if(new Set(products).size!==53) throw new Error(name+': expected 53 unique product routes, found '+new Set(products).size);

  // Whole-estate rendering: every product, every viewport, plus 200% text.
  for(const href of products){
    await baseline(page,href,name+' '+href);
    if((await page.locator('.service-breadcrumbs').count())!==1) throw new Error(name+' '+href+': breadcrumb missing');
    if((await page.locator('.service-context-nav').count())!==1) throw new Error(name+' '+href+': context nav missing');
    const body=(await page.locator('body').innerText()).toLowerCase();
    if(!body.includes('pricing') && !/£\s?\d/.test(body)) throw new Error(name+' '+href+': pricing information missing');
    await page.evaluate(()=>{document.body.style.fontSize='200%'});
    await noOverflow(page,name+' '+href+' 200%');
  }

  for(const href of reps){
    await page.goto(BASE+'/'+href,{waitUntil:'networkidle'});
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-rep-'+href.replace('.html','')+'.png',fullPage:true});
  }

  await baseline(page,'contact.html',name+' contact');
  if(await page.locator('form').count()!==1) throw new Error(name+': contact form count');
  await context.close();
}

for(const [v,n] of [[{width:1440,height:900},'desktop'],[{width:800,height:1280},'tablet'],[{width:390,height:844},'mobile'],[{width:320,height:900},'reflow-320']]) await run(v,n);
await browser.close();
console.log('PASS: 7-area catalogue hierarchy, all 53 service links and all 53 product pages pass desktop, tablet, mobile, 320px reflow and 200% text regression; mobile tap-return checks cover every catalogue service link');
