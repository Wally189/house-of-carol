import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const pages=[
  'worked-example-process-handover.html',
  'worked-example-trade-account-customer-journey.html',
  'worked-example-ai-workflow.html'
];
async function noOverflow(page,label){const d=await page.evaluate(()=>({w:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));if(d.scroll>d.w+1)throw new Error(label+': horizontal overflow '+JSON.stringify(d));}
async function a11y(page,label){const r=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();const bad=r.violations.filter(v=>v.impact==='serious'||v.impact==='critical');if(bad.length)throw new Error(label+': serious/critical accessibility violations '+bad.map(v=>v.id).join(', '));}
for(const [name,viewport] of [['desktop',{width:1440,height:900}],['laptop',{width:1024,height:768}],['mobile',{width:390,height:844}]]){
 const context=await browser.newContext({viewport});const page=await context.newPage();
 await page.goto(BASE+'/worked-examples.html',{waitUntil:'networkidle'});
 if(await page.locator('.worked-example-card').count()!==3)throw new Error(name+': expected three retained worked-example cards');
 await noOverflow(page,name+' worked-example index');if(name!=='laptop')await a11y(page,name+' worked-example index');
 await page.screenshot({path:'qa-artifacts/'+name+'-worked-examples.png',fullPage:true});
 for(const path of pages){
   await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});
   if(await page.locator('h1').count()!==1)throw new Error(name+' '+path+': H1 contract');
   const body=(await page.locator('body').innerText()).toLowerCase();
   for(const phrase of ['worked example','situation','what house of carol would look at','what a clearer state could look like','what the customer could receive','what might logically follow']){
     if(!body.includes(phrase))throw new Error(name+' '+path+': missing '+phrase);
   }
   if(!body.includes('not a customer testimonial or measured result'))throw new Error(name+' '+path+': evidence disclosure missing');
   await noOverflow(page,name+' '+path);if(name==='desktop'||name==='mobile')await a11y(page,name+' '+path);
 }
 await page.goto(BASE+'/'+pages[0],{waitUntil:'networkidle'});await page.screenshot({path:'qa-artifacts/'+name+'-worked-example-representative.png',fullPage:true});await context.close();
}
await browser.close();
console.log('PASS: retained worked-example index and all three worked examples pass desktop, laptop and mobile layout plus serious/critical accessibility checks.');
