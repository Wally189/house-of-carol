import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const EXPECTED_NAV=['index.html','how-it-works.html','catalogue.html','about.html','contact.html'];
const CORE_PAGES=['index.html','how-it-works.html','about.html','contact.html','privacy.html','terms.html','404.html'];
const AREA_PAGES=["catalogue-operations.html","catalogue-ai-digital.html","catalogue-commercial.html","catalogue-learning.html","catalogue-research.html","catalogue-charity-public.html","catalogue-church-parish.html"];
const EXAMPLE_PAGES=['worked-examples.html','worked-example-process-handover.html','worked-example-trade-account-customer-journey.html','worked-example-ai-workflow.html'];
const REMEDIATED_AREA_PAGES=new Set(['catalogue-operations.html','catalogue-ai-digital.html']);
const EXAMPLE_PRODUCT_PAGES=new Set(['process-design-sprint.html','customer-journey-and-service-operations-review.html','ai-workflow-opportunity-review.html','ai-workflow-implementation-sprint.html','ai-adoption-support-retainer.html']);
const REVIEW_SCREENSHOT_VIEWPORTS=new Set(['desktop','desktop-1024','tablet','mobile-760','mobile','mobile-360','reflow-320']);
const FOCUS_PRODUCT='process-design-sprint.html';
const FORM_ENDPOINT='https://formspree.io/f/mgvgrgvb';
const AREA_LINKS='.area-entry .area-card-link';
const SERVICE_LINKS='.service-entry .service-card-link';
let HEADER_REFERENCE=null;

async function noOverflow(page,label){
  const g=await page.evaluate(()=>{
    const w=document.documentElement.clientWidth;
    const clippedByAncestor=(el)=>{
      for(let p=el.parentElement;p;p=p.parentElement){
        const s=getComputedStyle(p); const r=p.getBoundingClientRect();
        const clipsX=s.overflowX==='hidden'||s.overflowX==='clip'||s.overflow==='hidden'||s.overflow==='clip';
        if(clipsX && r.left>=-1 && r.right<=w+1) return true;
      }
      return false;
    };
    const offenders=[...document.querySelectorAll('*')]
      .map(el=>{const r=el.getBoundingClientRect();return {el,tag:el.tagName,left:r.left,right:r.right,text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)}})
      .filter(x=>(x.right>w+1||x.left<-1) && !clippedByAncestor(x.el))
      .map(({tag,left,right,text})=>({tag,left,right,text})).slice(0,10);
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

async function stableHeaderAlignment(page,label){
  const state=await page.evaluate(()=>{
    const metric=(selector)=>{
      const el=document.querySelector(selector);
      if(!el) return null;
      const r=el.getBoundingClientRect();
      const round=(n)=>Math.round(n*10)/10;
      return {left:round(r.left),top:round(r.top),width:round(r.width),height:round(r.height)};
    };
    return {header:metric('.site-header'),brand:metric('.brand'),nav:metric('.main-nav')};
  });
  if(!state.header||!state.brand||!state.nav) throw new Error(label+': site header geometry unavailable '+JSON.stringify(state));
  if(!HEADER_REFERENCE){HEADER_REFERENCE=state;return;}
  const tolerance=1;
  for(const part of ['header','brand','nav']){
    for(const field of ['left','top','width','height']){
      if(Math.abs(state[part][field]-HEADER_REFERENCE[part][field])>tolerance){
        throw new Error(label+': menu/header alignment moved at '+part+'.'+field+'; expected '+HEADER_REFERENCE[part][field]+' got '+state[part][field]);
      }
    }
  }
}

async function compactCatalogueComposition(page,path,label,viewportWidth){
  if(path==='catalogue.html'){
    if(await page.locator('.customer-pathway-grid').count()!==0) throw new Error(label+': retired three-stage pathway UI is still present');
    if(await page.locator('.worked-example-card').count()!==0) throw new Error(label+': main catalogue must not expose worked-example cards');
    if(await page.locator('.worked-examples').count()!==0) throw new Error(label+': main catalogue must remain separate from worked examples');
    if(await page.locator('a[href="case-studies.html"]').count()!==0) throw new Error(label+': main catalogue must remain separate from the case-study index');
    const hero=page.locator('.catalogue-hero-visual img');
    if(await hero.count()!==1) throw new Error(label+': main catalogue must expose exactly one controlled hero illustration');
    const heroState=await hero.evaluate(img=>({alt:(img.getAttribute('alt')||'').trim()}));
    if(!heroState.alt) throw new Error(label+': main catalogue hero illustration requires useful alternative text');
    const cards=page.locator('.area-card-link');
    if(await cards.count()!==7) throw new Error(label+': main catalogue must expose exactly seven problem-led service-area choices');
    for(let i=0;i<await cards.count();i++){
      const state=await cards.nth(i).evaluate(el=>{
        const heading=el.querySelector('.area-card-heading'); const copy=el.querySelector('.area-card-copy'); const figure=el.querySelector('figure');
        const a=heading?.getBoundingClientRect(); const b=copy?.getBoundingClientRect();
        const overlaps=(x,y)=>!!(x&&y&&Math.min(x.right,y.right)-Math.max(x.left,y.left)>1&&Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>1);
        return {hasHeading:!!heading?.querySelector('h3'),hasProblem:!!copy?.querySelector('p'),hasFigure:!!figure,stacked:!!(a&&b&&Math.abs(a.left-b.left)<2&&b.top>=a.bottom-2),overlap:overlaps(a,b),width:el.getBoundingClientRect().width};
      });
      if(!state.hasHeading||!state.hasProblem) throw new Error(label+': service-area choice '+i+' is missing its heading or problem description '+JSON.stringify(state));
      if(state.hasFigure) throw new Error(label+': service-area choice '+i+' must remain text-led without per-area card imagery '+JSON.stringify(state));
      if(state.overlap) throw new Error(label+': service-area choice '+i+' has overlapping heading and problem text '+JSON.stringify(state));
      if(viewportWidth<=760&&!state.stacked) throw new Error(label+': service-area choice '+i+' is not a clear single-column mobile row '+JSON.stringify(state));
      if(state.width<240) throw new Error(label+': service-area choice '+i+' is implausibly narrow '+JSON.stringify(state));
    }
    if(viewportWidth<=760){
      const problem=await page.locator('.problem .content-grid').evaluate(el=>{const kids=[...el.children].map(x=>x.getBoundingClientRect());return kids.length<2||Math.abs(kids[0].left-kids[1].left)<2;});
      if(!problem) throw new Error(label+': closing CTA is not stacked at compact width');
    }
  }

  if(REMEDIATED_AREA_PAGES.has(path)){
    if(await page.locator('.catalogue-choice').count()!==0) throw new Error(label+': duplicative buyer-situation list remains');
    const expectedServices=path==='catalogue-operations.html'?10:15;
    const expectedHero=path==='catalogue-operations.html'?'assets/catalogue-operations.svg':'assets/catalogue-ai-digital.svg';
    const services=page.locator('.service-entry');
    if(await services.count()!==expectedServices) throw new Error(label+': expected '+expectedServices+' service choices');
    if(await page.locator('.service-entry figure').count()!==0) throw new Error(label+': service rows must remain text-led without decorative per-service imagery');
    if(await page.locator('.worked-examples').count()!==0) throw new Error(label+': selection page must not contain fictional worked-example cards');
    if(path==='catalogue-ai-digital.html' && await page.locator('.service-cluster').count()!==0) throw new Error(label+': legacy AI service clusters remain');
    if(await page.locator('.service-card-heading').count()!==expectedServices || await page.locator('.service-card-copy').count()!==expectedServices) throw new Error(label+': service heading/copy contract is incomplete');
    const hero=page.locator('.category-hero-visual img');
    if(await hero.count()!==1) throw new Error(label+': catalogue must expose one controlled category illustration');
    const heroState=await hero.evaluate(img=>({src:img.getAttribute('src'),alt:img.getAttribute('alt'),hidden:img.closest('figure')?.getAttribute('aria-hidden')}));
    if(heroState.src!==expectedHero||heroState.alt!==''||heroState.hidden!=='true') throw new Error(label+': category illustration is not the approved decorative asset '+JSON.stringify(heroState));
    for(let i=0;i<await services.count();i++){
      const state=await services.nth(i).locator('.service-card-link').evaluate(el=>{
        const heading=el.querySelector('.service-card-heading'); const copy=el.querySelector('.service-card-copy');
        const a=heading?.getBoundingClientRect(); const b=copy?.getBoundingClientRect();
        const overlaps=(x,y)=>!!(x&&y&&Math.min(x.right,y.right)-Math.max(x.left,y.left)>1&&Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>1);
        return {stacked:!!(a&&b&&Math.abs(a.left-b.left)<2&&b.top>=a.bottom-2),overlap:overlaps(a,b)};
      });
      if(state.overlap) throw new Error(label+': service '+i+' has overlapping text regions '+JSON.stringify(state));
      if(viewportWidth<=860&&!state.stacked) throw new Error(label+': service '+i+' is not a clear single-column compact row '+JSON.stringify(state));
    }
  }
}

async function compactProductComposition(page,path,label,viewportWidth){
  if(viewportWidth>1100 || await page.locator('body.canonical-product-page').count()===0) return;
  const hero=await page.locator('.product-hero>.shell').evaluate(el=>{
    const kids=[...el.children].slice(0,2).map(x=>x.getBoundingClientRect());
    return kids.length<2||Math.abs(kids[0].left-kids[1].left)<2&&kids[1].top>=kids[0].bottom-2;
  });
  if(!hero) throw new Error(label+': canonical product hero remains a compressed multi-column layout');
  const grids=page.locator('.recognition-grid,.deliverable-groups');
  for(let i=0;i<await grids.count();i++){
    const tracks=await grids.nth(i).evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length);
    if(tracks>1) throw new Error(label+': product card grid '+i+' remains multi-column at compact width');
  }
  if(EXAMPLE_PRODUCT_PAGES.has(path) && await page.locator('.worked-example-promo').count()!==1) throw new Error(label+': relevant product page is not connected to a worked example');
}

async function baseline(page,path,label,runAccessibility,viewportWidth){
  const response=await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});
  if(!response||!response.ok()) throw new Error(label+': HTTP '+response?.status());
  if(await page.locator('h1').count()!==1) throw new Error(label+': H1 count');
  const nav=await page.locator('.main-nav a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
  if(JSON.stringify(nav)!==JSON.stringify(EXPECTED_NAV)) throw new Error(label+': nav '+JSON.stringify(nav));
  await stableHeaderAlignment(page,label);
  await noOverflow(page,label);
  await compactCatalogueComposition(page,path,label,viewportWidth);
  await compactProductComposition(page,path,label,viewportWidth);
  if(runAccessibility) await noSeriousAccessibilityDefects(page,label);
}

async function tapAllAndReturn(page,selector,label){
  const count=await page.locator(selector).count();
  for(let i=0;i<count;i++){
    const link=page.locator(selector).nth(i); const href=await link.getAttribute('href');
    if(!href) throw new Error(label+': missing href at '+i);
    const expected=new URL(href,page.url()).href;
    await Promise.all([page.waitForURL(expected),link.tap()]);
    if(page.url()!==expected) throw new Error(label+': tap did not navigate to '+href);
    await page.goBack({waitUntil:'networkidle'});
    await noStickyInset(page.locator(selector).nth(i),label+' return '+href);
  }
}

async function run(viewport,name){
  HEADER_REFERENCE=null;
  const context=await browser.newContext({viewport,hasTouch:name==='mobile'||name==='mobile-360'||name==='reflow-320'}); const page=await context.newPage();
  const runAccessibility=name==='desktop'||name==='mobile';
  for(const core of CORE_PAGES){
    await baseline(page,core,name+' '+core,runAccessibility,viewport.width);
    if(core==='contact.html'){
      const enquiry=page.locator('form[aria-label="Website enquiry form"]');
      const callRequest=page.locator('form[aria-label="Introductory call request form"]');
      if(await page.locator('form').count()!==2 || await enquiry.count()!==1 || await callRequest.count()!==1) throw new Error(name+': contact form count');
      if(await enquiry.getAttribute('action')!==FORM_ENDPOINT || await callRequest.getAttribute('action')!==FORM_ENDPOINT) throw new Error(name+': contact form endpoint');
      if(await page.locator('form fieldset[disabled]').count()!==0) throw new Error(name+': contact form fieldset remains held');
      if(await page.locator('form button[type="submit"][disabled]').count()!==0) throw new Error(name+': contact submit button remains held');
      if(await enquiry.locator('input[required], textarea[required]').count()!==3) throw new Error(name+': enquiry required controls');
      if(await callRequest.locator('input[type="radio"][name="preferred_call_time"]').count()!==4) throw new Error(name+': call-request time option count');
      if(await callRequest.locator('input[type="radio"][name="preferred_call_time"][required]').count()!==1) throw new Error(name+': call-request time group required state');
      if(await callRequest.locator('input[required], textarea[required]').count()!==4) throw new Error(name+': call-request required controls');
    }
    if(name==='desktop'||name==='mobile') await page.screenshot({path:'qa-artifacts/'+name+'-'+core.replace('.html','')+'.png',fullPage:true});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'}); await noOverflow(page,name+' '+core+' 200%');
  }

  await baseline(page,'catalogue.html',name+' catalogue',runAccessibility,viewport.width);
  if((await page.locator(AREA_LINKS).count())!==7) throw new Error(name+': main catalogue area count');
  if((await page.locator('.service-entry').count()!==0)) throw new Error(name+': main catalogue exposes service entries');
  if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+': main catalogue displays a price');
  if(name==='mobile') await tapAllAndReturn(page,AREA_LINKS,name+' main catalogue');
  await page.screenshot({path:'qa-artifacts/'+name+'-catalogue.png',fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'}); await noOverflow(page,name+' catalogue 200%');

  const products=[]; const reps=[];
  for(const area of AREA_PAGES){
    await baseline(page,area,name+' '+area,runAccessibility,viewport.width);
    const serviceCount=await page.locator(SERVICE_LINKS).count(); if(serviceCount<1) throw new Error(name+' '+area+': no service links');
    if((await page.locator('body').innerText()).match(/£\s?\d/)) throw new Error(name+' '+area+': area displays a price');
    const hrefs=await page.locator(SERVICE_LINKS).evaluateAll(a=>a.map(x=>x.getAttribute('href'))); products.push(...hrefs); reps.push(hrefs[0]);
    if(name==='mobile') await tapAllAndReturn(page,SERVICE_LINKS,name+' '+area);
    if(REVIEW_SCREENSHOT_VIEWPORTS.has(name)) await page.screenshot({path:'qa-artifacts/'+name+'-'+area.replace('.html','')+'.png',fullPage:true});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'}); await noOverflow(page,name+' '+area+' 200%');
  }
  if(new Set(products).size!==54) throw new Error(name+': expected 54 unique product routes, found '+new Set(products).size);

  for(const href of products){
    await baseline(page,href,name+' '+href,runAccessibility,viewport.width);
    if((await page.locator('.service-breadcrumbs').count())!==1) throw new Error(name+' '+href+': breadcrumb missing');
    if((await page.locator('.service-context-nav').count())!==1) throw new Error(name+' '+href+': context nav missing');
    const body=(await page.locator('body').innerText()).toLowerCase(); if(!body.includes('pricing')&&!/£\s?\d/.test(body)) throw new Error(name+' '+href+': pricing information missing');
    if(href===FOCUS_PRODUCT&&REVIEW_SCREENSHOT_VIEWPORTS.has(name)) await page.screenshot({path:'qa-artifacts/'+name+'-process-design-sprint.png',fullPage:true});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'}); await noOverflow(page,name+' '+href+' 200%');
  }

  for(const href of EXAMPLE_PAGES){
    await baseline(page,href,name+' '+href,runAccessibility,viewport.width);
    const body=(await page.locator('body').innerText()).toLowerCase();
    if(href==='worked-examples.html'){
      if(!body.includes('worked example')) throw new Error(name+' '+href+': worked-example index terminology missing');
    }else if(!body.includes('illustrative example')||!body.includes('not a customer testimonial or measured result')){
      throw new Error(name+' '+href+': evidence-honest worked-example disclosure missing');
    }
    if(['desktop','mobile'].includes(name)) await page.screenshot({path:'qa-artifacts/'+name+'-'+href.replace('.html','')+'.png',fullPage:true});
  }

  for(const href of reps){
    await page.goto(BASE+'/'+href,{waitUntil:'networkidle'});
    if(REVIEW_SCREENSHOT_VIEWPORTS.has(name)) await page.screenshot({path:'qa-artifacts/'+name+'-rep-'+href.replace('.html','')+'.png',fullPage:true});
  }
  await context.close();
}

const VIEWPORTS=[[{width:1440,height:900},'desktop'],[{width:1280,height:800},'desktop-1280'],[{width:1024,height:768},'desktop-1024'],[{width:800,height:1280},'tablet'],[{width:760,height:1000},'mobile-760'],[{width:430,height:932},'mobile-430'],[{width:390,height:844},'mobile'],[{width:360,height:800},'mobile-360'],[{width:320,height:900},'reflow-320']];
for(const [v,n] of VIEWPORTS) await run(v,n);
await browser.close();
console.log('PASS: problem-led main catalogue remains separate from case studies and worked examples; seven text-led service-area choices, non-duplicative problem-led Operations and AI service areas, 54 canonical product pages and worked-example journeys pass browser regression at 1440, 1280, 1024, 800, 760, 430, 390, 360 and 320px plus 200% text reflow; site-header, brand and primary-menu geometry remain aligned across pages within each viewport; compact layouts stack rather than compress; approved category illustrations remain controlled and decorative; active Formspree enquiry and call-request forms remain accessible and enabled; serious/critical axe checks cover desktop and 390px mobile.');