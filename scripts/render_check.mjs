import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const BASE='http://127.0.0.1:8000'; const browser=await chromium.launch({headless:true}); await fs.mkdir('qa-artifacts',{recursive:true});
async function noOverflow(page,label){const g=await page.evaluate(()=>({c:document.documentElement.clientWidth,s:document.documentElement.scrollWidth}));if(g.s>g.c+1)throw new Error(`${label}: overflow ${JSON.stringify(g)}`)}
async function run(viewport,name){
 const context=await browser.newContext({viewport}); const page=await context.newPage(); await page.goto(`${BASE}/index.html`,{waitUntil:'networkidle'}); await page.locator('h1').waitFor();
 const body=await page.locator('body').innerText(); for(const x of ['We build useful businesses.','What we build','How we work','Our businesses and ventures','Contact']) if(!body.includes(x)) throw new Error(`${name}: missing ${x}`);
 if(await page.locator('form').count()!==1) throw new Error(`${name}: contact form count`); for(const id of ['name','email','message']) if(!await page.locator(`#${id}`).isVisible()) throw new Error(`${name}: missing ${id}`);
 await noOverflow(page,name); await page.screenshot({path:`qa-artifacts/${name}-home.png`,fullPage:true}); await page.evaluate(()=>{document.documentElement.style.fontSize='200%'}); await noOverflow(page,`${name} 200%`);
 for(const path of ['privacy.html','terms.html']){await page.goto(`${BASE}/${path}`);await page.locator('h1').waitFor();await noOverflow(page,`${name} ${path}`)} await context.close();
}
for(const [v,n] of [[{width:1440,height:900},'desktop'],[{width:800,height:1280},'tablet'],[{width:390,height:844},'mobile'],[{width:320,height:900},'reflow-320']]) await run(v,n);
await browser.close(); console.log('PASS: contact/legal journey renders across desktop, tablet, mobile and 200% text');
