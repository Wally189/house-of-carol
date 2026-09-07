import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE='http://127.0.0.1:8000';
const browser=await chromium.launch({headless:true});
await fs.mkdir('qa-artifacts',{recursive:true});

async function noOverflow(page,label){
  const g=await page.evaluate(()=>({c:document.documentElement.clientWidth,s:document.documentElement.scrollWidth}));
  if(g.s>g.c+1) throw new Error(`${label}: overflow ${JSON.stringify(g)}`);
}

async function openAndCheck(page,path,label,required){
  const response=await page.goto(`${BASE}/${path}`,{waitUntil:'networkidle'});
  if(!response || !response.ok()) throw new Error(`${label}: response ${response?.status()}`);
  await page.locator('h1').waitFor();
  if(await page.locator('h1').count()!==1) throw new Error(`${label}: expected one h1`);
  const body=await page.locator('body').innerText();
  for(const phrase of required) if(!body.includes(phrase)) throw new Error(`${label}: missing ${phrase}`);
  await noOverflow(page,label);
}

async function run(viewport,name){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();

  await openAndCheck(page,'index.html',`${name} home`,[
    'A useful place for difficult business work.',
    'Start with the job, not the jargon.',
    'Products & services',
    'Bring us a problem'
  ]);
  if(await page.locator('form').count()!==1) throw new Error(`${name}: contact form count`);
  for(const id of ['name','email','message']) if(!await page.locator(`#${id}`).isVisible()) throw new Error(`${name}: missing ${id}`);
  await page.screenshot({path:`qa-artifacts/${name}-home.png`,fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  await noOverflow(page,`${name} home 200%`);

  await openAndCheck(page,'catalogue.html',`${name} catalogue`,[
    'Useful work, with a clear boundary.',
    'One important business process, properly sorted out.',
    '£1,500',
    'Not yet released as a fixed offer'
  ]);
  await page.screenshot({path:`qa-artifacts/${name}-catalogue.png`,fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  await noOverflow(page,`${name} catalogue 200%`);

  await openAndCheck(page,'process-design-sprint.html',`${name} HOC-015`,[
    "Your business shouldn't depend on one person remembering how everything works.",
    '£1,500',
    'Before and after should be obvious.',
    'Worth buying only when the problem is real.',
    'A real person accountable for the result.'
  ]);
  await page.screenshot({path:`qa-artifacts/${name}-hoc015.png`,fullPage:true});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  await noOverflow(page,`${name} HOC-015 200%`);

  for(const path of ['about.html','privacy.html','terms.html']){
    await openAndCheck(page,path,`${name} ${path}`,[]);
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
    await noOverflow(page,`${name} ${path} 200%`);
  }
  await context.close();
}

for(const [viewport,name] of [
  [{width:1440,height:900},'desktop'],
  [{width:800,height:1280},'tablet'],
  [{width:390,height:844},'mobile'],
  [{width:320,height:900},'reflow-320'],
]) await run(viewport,name);

await browser.close();
console.log('PASS: current House, catalogue and HOC-015 render across desktop, tablet, mobile, 320px reflow and 200% text');
