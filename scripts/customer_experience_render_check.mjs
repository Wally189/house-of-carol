import { chromium } from "playwright";
import fs from "fs";
const txt=fs.readFileSync("scripts/build_case_studies.py","utf8"); const block=txt.match(/PRODUCTS = \[(.*?)\]\n/s)?.[1]||""; const routes=[...block.matchAll(/'([^']+\.html)'/g)].map(m=>m[1]); if(routes.length!==53) throw new Error(`Expected 53 routes, got ${routes.length}`);
const browser=await chromium.launch({headless:true}); const page=await browser.newPage(); const defects=[];
for(const vp of [{n:"desktop",width:1440,height:1000},{n:"mobile",width:390,height:844}]){
  await page.setViewportSize(vp);
  for(const route of routes){
    const before=defects.length;
    const res=await page.goto(`http://127.0.0.1:8000/${route}`,{waitUntil:"domcontentloaded"});
    if(!res||res.status()!=200){defects.push(`${route} ${vp.n}: http`); continue;}
    const x=await page.evaluate(()=>({h1:document.querySelectorAll("h1").length,visual:document.querySelectorAll("figure.customer-service-visual img").length,order:document.querySelectorAll(".customer-order-journey").length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,text:(" "+document.body.innerText.toLowerCase()+" ")}));
    if(x.h1!==1)defects.push(`${route} ${vp.n}: H1`);
    if(x.visual!==1)defects.push(`${route} ${vp.n}: visual`);
    if(x.order!==1)defects.push(`${route} ${vp.n}: order`);
    if(x.overflow)defects.push(`${route} ${vp.n}: overflow`);
    for(const t of ["customer 000","external proof required","internal qa","first-test","scope fit","service unit","governance kernel","source universe","temporal service"," bounded "]) if(x.text.includes(t)) defects.push(`${route} ${vp.n}: ${t.trim()}`);
    if(defects.length===before) console.log(`PASS: ${route} — ${vp.n}`);
  }
}
await browser.close();
if(defects.length){console.error("CUSTOMER EXPERIENCE BROWSER QA: FAIL"); defects.forEach(x=>console.error("- "+x)); process.exit(1);}
console.log("CUSTOMER EXPERIENCE BROWSER QA: PASS — 53/53 at desktop and mobile.");
