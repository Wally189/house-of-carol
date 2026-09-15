import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});
const reps=['case-study-process-design-sprint.html','case-study-ai-data-use-rules-sprint.html','case-study-invoice-to-cash-process-setup.html','case-study-bespoke-organisational-training-design.html','case-study-research-briefing.html','case-study-charity-ai-governance-pack-and-implementation.html','case-study-church-and-parish-grant-funding-research.html'];
async function noOverflow(page,label){const d=await page.evaluate(()=>({w:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));if(d.scroll>d.w+1)throw new Error(label+': horizontal overflow '+JSON.stringify(d));}
async function a11y(page,label){const r=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();const bad=r.violations.filter(v=>v.impact==='serious'||v.impact==='critical');if(bad.length)throw new Error(label+': serious/critical accessibility violations '+bad.map(v=>v.id).join(', '));}
for(const [name,viewport] of [['desktop',{width:1440,height:900}],['laptop',{width:1024,height:768}],['mobile',{width:390,height:844}]]){
 const context=await browser.newContext({viewport});const page=await context.newPage();
 await page.goto(BASE+'/case-studies.html',{waitUntil:'networkidle'});
 const count=await page.locator('.case-study-link').count();if(count!==53)throw new Error(name+': expected 53 case-study links, found '+count);
 if(await page.locator('.case-family-head').count()!==7)throw new Error(name+': expected seven case-study families');
 await noOverflow(page,name+' case index');if(name!=='laptop')await a11y(page,name+' case index');
 await page.screenshot({path:'qa-artifacts/'+name+'-case-studies.png',fullPage:true});
 for(const path of reps){await page.goto(BASE+'/'+path,{waitUntil:'networkidle'});if(await page.locator('h1').count()!==1)throw new Error(name+' '+path+': H1 contract');const hero=page.locator('.case-study-hero-visual img');if(await hero.count()!==1||!(await hero.isVisible()))throw new Error(name+' '+path+': hero image missing');const disclosure=(await page.locator('.case-disclosure').innerText()).toLowerCase();if(!disclosure.includes('not a real customer'))throw new Error(name+' '+path+': evidence disclosure missing');if(await page.locator('.case-output').count()<3)throw new Error(name+' '+path+': case outputs too thin');if(await page.locator('.case-next a').count()<3)throw new Error(name+' '+path+': decision routes incomplete');await noOverflow(page,name+' '+path);if(name==='desktop'||name==='mobile')await a11y(page,name+' '+path);}
 await page.goto(BASE+'/'+reps[0],{waitUntil:'networkidle'});await page.screenshot({path:'qa-artifacts/'+name+'-case-study-representative.png',fullPage:true});await context.close();
}
await browser.close();
console.log('PASS: case-study index and seven family representatives pass 1440px desktop, 1024px laptop and 390px mobile layout; 53 routes visible; imagery, evidence disclosure, navigation and serious/critical accessibility checks pass.');
