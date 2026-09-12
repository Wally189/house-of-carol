import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const CORE_PAGES=['index.html','how-it-works.html','catalogue.html','about.html','contact.html','privacy.html','terms.html'];
const AREA_PAGES=["catalogue-operations.html","catalogue-ai-digital.html","catalogue-commercial.html","catalogue-learning.html","catalogue-research.html","catalogue-charity-public.html","catalogue-church-parish.html"];
const LCP_GOOD_MS=2500;
const CLS_GOOD=0.1;

async function representativeProducts(){
  const reps=[];
  for(const area of AREA_PAGES){
    const html=await fs.readFile(area,'utf8');
    const match=html.match(/class="service-card-link" href="([^"]+\.html)"/i);
    if(!match) throw new Error(area+': representative product route not found');
    reps.push(match[1]);
  }
  return reps;
}

const PAGES=[...new Set([...CORE_PAGES,...AREA_PAGES,...await representativeProducts(),'shared-drive-cleanup.html'])];
const browser=await chromium.launch({headless:true});
const results=[];
const failures=[];

async function run(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  await page.addInitScript(()=>{
    window.__hocPerf={lcp:0,cls:0};
    try {
      new PerformanceObserver(list=>{
        for(const entry of list.getEntries()) window.__hocPerf.lcp=Math.max(window.__hocPerf.lcp,entry.startTime||0);
      }).observe({type:'largest-contentful-paint',buffered:true});
    } catch {}
    try {
      new PerformanceObserver(list=>{
        for(const entry of list.getEntries()) if(!entry.hadRecentInput) window.__hocPerf.cls+=entry.value||0;
      }).observe({type:'layout-shift',buffered:true});
    } catch {}
  });

  for(const path of PAGES){
    const response=await page.goto(`${BASE}/${path}`,{waitUntil:'networkidle'});
    if(!response||!response.ok()){
      failures.push(`${name} ${path}: HTTP ${response?.status()}`);
      continue;
    }
    await page.waitForTimeout(150);
    const data=await page.evaluate(()=>{
      const nav=performance.getEntriesByType('navigation')[0];
      const resources=performance.getEntriesByType('resource').map(r=>({name:r.name,transferSize:r.transferSize||0}));
      const fallbackLcp=performance.getEntriesByType('largest-contentful-paint').at(-1)?.startTime||0;
      return {
        lcp: Math.max(window.__hocPerf?.lcp||0,fallbackLcp),
        cls: window.__hocPerf?.cls||0,
        load: nav?.loadEventEnd||0,
        transfer: resources.reduce((sum,r)=>sum+r.transferSize,0),
        resources,
      };
    });
    const external=data.resources.filter(r=>{
      try { return new URL(r.name).origin!==new URL(BASE).origin; }
      catch { return false; }
    });
    if(data.lcp<=0) failures.push(`${name} ${path}: synthetic LCP unavailable`);
    if(data.lcp>LCP_GOOD_MS) failures.push(`${name} ${path}: synthetic LCP ${data.lcp.toFixed(1)}ms exceeds ${LCP_GOOD_MS}ms guard`);
    if(data.cls>CLS_GOOD) failures.push(`${name} ${path}: synthetic CLS ${data.cls.toFixed(3)} exceeds ${CLS_GOOD} guard`);
    if(external.length) failures.push(`${name} ${path}: unexpected runtime external resources ${JSON.stringify(external.map(r=>r.name))}`);
    results.push({viewport:name,path,lcp_ms:Number(data.lcp.toFixed(1)),cls:Number(data.cls.toFixed(3)),load_ms:Number(data.load.toFixed(1)),resource_transfer_bytes:data.transfer});
  }
  await context.close();
}

await run({width:1440,height:900},'desktop');
await run({width:390,height:844},'mobile');
await browser.close();

if(failures.length){
  console.error('PERFORMANCE REGRESSION: FAIL');
  for(const failure of failures) console.error('- '+failure);
  process.exit(1);
}

const worstLcp=[...results].sort((a,b)=>b.lcp_ms-a.lcp_ms)[0];
const worstCls=[...results].sort((a,b)=>b.cls-a.cls)[0];
console.log(`PASS: synthetic local performance guard covered ${PAGES.length} representative/core routes on desktop and mobile`);
console.log(`Worst synthetic LCP: ${worstLcp.lcp_ms}ms (${worstLcp.viewport} ${worstLcp.path}); guard ${LCP_GOOD_MS}ms`);
console.log(`Worst synthetic CLS: ${worstCls.cls} (${worstCls.viewport} ${worstCls.path}); guard ${CLS_GOOD}`);
console.log('Boundary: this is a repeatable pre-release regression guard, not field Core Web Vitals evidence or a claim about real-user performance.');
