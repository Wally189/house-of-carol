import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';

// HOC-019 bounded responsive acceptance coverage.
const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const EXPECTED_NAV=['index.html','how-it-works.html','catalogue.html','about.html','contact.html'];
const CORE_PAGES=['index.html','how-it-works.html','about.html','contact.html','privacy.html','terms.html','404.html'];
const AREA_PAGES=["catalogue-operations.html","catalogue-ai-digital.html","catalogue-commercial.html","catalogue-learning.html","catalogue-research.html","catalogue-charity-public.html","catalogue-church-parish.html"];
const AREA_LINKS='.area-entry .area-card-link';
const SERVICE_LINKS='.service-entry .service-card-link';

async function noOverflow(page,label){
  const g=await page.evaluate(()=>{
    const w=document.documentElement.clientWidth;
    const clippedByAncestor=(el)=>{
      for(let p=el.parentElement;p;p=p.parentElement){
        const s=getComputedStyle(p);
        const r=p.getBoundingClientRect();
        const clipsX=s.overflowX==='hidden'||s.overflowX==='clip'||s.overflow==='hidden'||s.overflow==='clip';
        if(clipsX && r.left>=-1 && r.right<=w+1) return true;
      }
      return false;
    };
    const offenders=[...document.querySelectorAll('*')]
      .map(el=>{const r=el.getBoundingClientRect();return {el,tag:el.tagName,left:r.left,right:r.right,text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)}})
      .filter(x=>(x.right>w+1||x.left<-1) && !clippedByAncestor(x.el))
      .map(({tag,left,right,text})=>({tag,left,right,text}))
      .slice(0,10);
    return {w,offenders};
  });
  if(g.offenders.length) throw new Error(label+': visible overflow '+JSON.stringify(g));
}

async function noSeriousAccessibilityDefects(page,label){
  const results=await new AxeBuilder({page}).analyze();
  const material=results.violations.filter(v=>v.impact==='critical'||v.impact==='serious');
  if(material.length){
    const summary=material.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.length}));
    throw new Error(label+': serious/critical accessibility violations '+JSON.stringify(summary));
  }
}

async function noStickyInset(locator,label){
  const shadow=await locator.evaluate(el=>getComputedStyle(el).boxShadow);
  if(shadow!=='none') throw new Error(label+': touch navigation left an inset/hover shadow '+shadow);
}

async function baseline(page,path,label,runAccessibility){
  const response=await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});
  if(!response||!response.ok()) throw new Error(label+': HTTP '+response?.status());
  if(await page.locator('h1').count()!==1) throw new Error(label+': H1 count');
  const nav=await page.locator('.main-nav a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
  if(JSON.stringify(nav)!==JSON.stringify(EXPECTED_NAV)) throw new Error(label+': nav '+JSON.stringify(nav));
  await noOverflow(page,label);
  if(runAccessibility) await noSeriousAccessibilityDefects(page,label);
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

async function hoc019ResponsiveCheck(viewport){
  const {width,height}=viewport;
  const label='hoc019-'+width;
  const context=await browser.newContext({viewport,hasTouch:width<=760});
  const page=await context.newPage();
  await baseline(page,'customer-support-knowledge-base-build.html',label,false);

  const state=await page.evaluate(()=>{
    const rect=(el)=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
    const heroShell=document.querySelector('.product-hero>.shell');
    const identity=document.querySelector('.product-hero-identity');
    const offer=document.querySelector('.product-hero-offer');
    const grid=document.querySelector('.deliverable-groups');
    const cards=[...grid.querySelectorAll('.product-card')];
    const wrappingTargets=[...document.querySelectorAll('.product-price strong,.product-price span,.product-trust-line,.product-trust-line strong,.product-scope-line,.product-turnaround,.product-audience,.deliverable-groups .product-card h3,.deliverable-groups .product-card p,.service-facts dt,.service-facts dd')];
    const badWrapping=wrappingTargets.map(el=>({text:(el.textContent||'').trim().slice(0,80),wordBreak:getComputedStyle(el).wordBreak,overflowWrap:getComputedStyle(el).overflowWrap})).filter(x=>x.wordBreak!=='normal'||x.overflowWrap==='anywhere');
    return {
      heroShell:rect(heroShell),
      identity:rect(identity),
      offer:rect(offer),
      heroColumns:getComputedStyle(heroShell).gridTemplateColumns,
      cardCount:cards.length,
      card7:cards[6]?rect(cards[6]):null,
      card8:cards[7]?rect(cards[7]):null,
      card7Title:cards[6]?.querySelector('h3')?.textContent?.trim()||'',
      card8Title:cards[7]?.querySelector('h3')?.textContent?.trim()||'',
      badWrapping
    };
  });

  if(state.cardCount!==8) throw new Error(label+': expected 8 deliverable cards, found '+state.cardCount);
  if(state.card7Title!=='Maintenance process and handover'||state.card8Title!=='Final factual correction') throw new Error(label+': card 7/8 source order changed '+JSON.stringify({card7:state.card7Title,card8:state.card8Title}));
  if(state.badWrapping.length) throw new Error(label+': unsafe word-breaking styles '+JSON.stringify(state.badWrapping));

  const stackExpected=width<=1040;
  const heroStacked=state.offer.top>=state.identity.bottom-1;
  if(stackExpected&&!heroStacked) throw new Error(label+': hero should stack before tablet/mobile cramping '+JSON.stringify(state));
  if(!stackExpected&&heroStacked) throw new Error(label+': desktop hero unexpectedly stacked '+JSON.stringify(state));

  if(stackExpected){
    const rowGap=state.offer.top-state.identity.bottom;
    const bottomGap=state.heroShell.bottom-state.offer.bottom;
    const minimumReadable=Math.min(600,state.heroShell.width*.75);
    if(rowGap<16||rowGap>48) throw new Error(label+': hero row gap is not normal document flow '+rowGap);
    if(bottomGap>80) throw new Error(label+': unexplained blank space remains below stacked offer '+bottomGap);
    if(state.offer.width<minimumReadable) throw new Error(label+': stacked offer remains unnaturally narrow '+JSON.stringify({offerWidth:state.offer.width,minimumReadable}));
  }else{
    if(Math.abs(state.offer.top-state.identity.top)>4||state.offer.left<=state.identity.left+40) throw new Error(label+': desktop hero columns are not coherent '+JSON.stringify(state));
  }

  if(width>760){
    if(Math.abs(state.card7.top-state.card8.top)>2) throw new Error(label+': final two cards are not on the same grid row '+JSON.stringify({card7:state.card7,card8:state.card8}));
    if(state.card8.left<=state.card7.left+40) throw new Error(label+': final factual correction is not in the right grid column '+JSON.stringify({card7:state.card7,card8:state.card8}));
  }else{
    if(state.card8.top<state.card7.bottom-1) throw new Error(label+': final two cards do not stack in source order '+JSON.stringify({card7:state.card7,card8:state.card8}));
    if(Math.abs(state.card7.left-state.card8.left)>2) throw new Error(label+': single-column cards are not aligned '+JSON.stringify({card7:state.card7,card8:state.card8}));
  }

  await noOverflow(page,label+' final');
  await page.screenshot({path:'qa-artifacts/'+label+'.png',fullPage:true});
  await context.close();
}

async function run(viewport,name){
  const context=await browser.newContext({viewport,hasTouch:name==='mobile'||name==='reflow-320'});
  const page=await context.newPage();
  const runAccessibility=name==='desktop'||name==='mobile';

  for(const core of CORE_PAGES){
    await baseline(page,core,name+' '+core,runAccessibility);
    if(core==='contact.html'){
      if(await page.locator('form').count()!==1) throw new Error(name+': contact form count');
      if(await page.locator('form fieldset[disabled]').count()!==1) throw new Error(name+': held contact form fieldset');
      if(await page.locator('form button[type="submit"][disabled]').count()!==1) throw new Error(name+': held contact submit button');
    }
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-'+core.replace('.html','')+'.png',fullPage:true});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
    await noOverflow(page,name+' '+core+' 200%');
  }

  await baseline(page,'catalogue.html',name+' catalogue',runAccessibility);
  if((await page.locator(AREA_LINKS).count())!==7) throw new Error(name+': main catalogue area count');
  if((await page.locator('.service-entry').count())!==0) throw new Error(name+': main catalogue exposes service entries');
  if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+': main catalogue displays a price');
  if(name==='mobile') await tapAllAndReturn(page,AREA_LINKS,name+' main catalogue');
  await page.screenshot({path:'qa-artifacts/'+name+'-catalogue.png',fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  await noOverflow(page,name+' catalogue 200%');

  const products=[];
  const reps=[];
  for(const area of AREA_PAGES){
    await baseline(page,area,name+' '+area,runAccessibility);
    const serviceCount=await page.locator(SERVICE_LINKS).count();
    if(serviceCount<1) throw new Error(name+' '+area+': no service links');
    if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+' '+area+': area displays a price');
    const hrefs=await page.locator(SERVICE_LINKS).evaluateAll(a=>a.map(x=>x.getAttribute('href')));
    products.push(...hrefs);
    reps.push(hrefs[0]);
    if(name==='mobile') await tapAllAndReturn(page,SERVICE_LINKS,name+' '+area);
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-'+area.replace('.html','')+'.png',fullPage:true});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
    await noOverflow(page,name+' '+area+' 200%');
  }

  if(new Set(products).size!==53) throw new Error(name+': expected 53 unique product routes, found '+new Set(products).size);

  for(const href of products){
    await baseline(page,href,name+' '+href,runAccessibility);
    if((await page.locator('.service-breadcrumbs').count())!==1) throw new Error(name+' '+href+': breadcrumb missing');
    if((await page.locator('.service-context-nav').count())!==1) throw new Error(name+' '+href+': context nav missing');
    const body=(await page.locator('body').innerText()).toLowerCase();
    if(!body.includes('pricing') && !/£\s?\d/.test(body)) throw new Error(name+' '+href+': pricing information missing');
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
    await noOverflow(page,name+' '+href+' 200%');
  }

  for(const href of reps){
    await page.goto(BASE+'/'+href,{waitUntil:'networkidle'});
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-rep-'+href.replace('.html','')+'.png',fullPage:true});
  }

  await context.close();
}

const VIEWPORTS=[
  [{width:1440,height:900},'desktop'],
  [{width:1280,height:800},'desktop-1280'],
  [{width:1024,height:768},'desktop-1024'],
  [{width:800,height:1280},'tablet'],
  [{width:760,height:1000},'mobile-760'],
  [{width:430,height:932},'mobile-430'],
  [{width:390,height:844},'mobile'],
  [{width:320,height:900},'reflow-320'],
];
for(const [v,n] of VIEWPORTS) await run(v,n);

const HOC019_VIEWPORTS=[
  {width:320,height:900},
  {width:360,height:900},
  {width:390,height:844},
  {width:412,height:915},
  {width:768,height:1024},
  {width:800,height:1280},
  {width:1024,height:768},
  {width:1440,height:900},
];
for(const viewport of HOC019_VIEWPORTS) await hoc019ResponsiveCheck(viewport);

await browser.close();
console.log('PASS: core pages, 7-area catalogue hierarchy and all 53 product pages pass browser regression at 1440x900, 1280x800, 1024x768, 800x1280, 760x1000, 430x932, 390x844 and 320x900 plus 200% text reflow; serious/critical axe checks cover every core, catalogue, area and product page on desktop and 390px mobile; mobile tap-return checks cover every catalogue service link; HOC-019 specific responsive assertions pass at 320, 360, 390, 412, 768, 800, 1024 and 1440px.');
