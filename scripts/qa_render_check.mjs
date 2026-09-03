import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const BASE='http://127.0.0.1:8000/qa';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts/storefront',{recursive:true});
async function noOverflow(page,label){const g=await page.evaluate(()=>({c:document.documentElement.clientWidth,s:document.documentElement.scrollWidth}));if(g.s>g.c+1)throw new Error(`${label}: overflow ${JSON.stringify(g)}`)}
async function run(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  await page.goto(`${BASE}/index.html`,{waitUntil:'networkidle'});
  await page.locator('h1').waitFor();
  const body=await page.locator('body').innerText();
  for(const x of ['Important business work, given proper attention.','Tender Decision & Submission Review','How it works','QA PREVIEW · NOT OPEN FOR ORDERS']) if(!body.includes(x)) throw new Error(`${name}: missing ${x}`);
  if(await page.locator('form').count()!==0) throw new Error(`${name}: live form unexpectedly present`);
  await noOverflow(page,name);
  await page.screenshot({path:`qa-artifacts/storefront/${name}.png`,fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  await noOverflow(page,`${name} 200%`);
  await page.screenshot({path:`qa-artifacts/storefront/${name}-text-200.png`,fullPage:true});
  await context.close();
}
for(const [v,n] of [[{width:1440,height:900},'desktop'],[{width:800,height:1280},'tablet'],[{width:390,height:844},'mobile'],[{width:320,height:900},'reflow-320']]) await run(v,n);
await browser.close();
console.log('PASS: QA storefront renders across desktop, tablet, mobile, 320px reflow and 200% text');
