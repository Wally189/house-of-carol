import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1200, height: 900 },
  hasTouch: true,
  isMobile: true,
  deviceScaleFactor: 1
});
const page = await context.newPage();
await fs.mkdir('qa-artifacts', { recursive: true });

await page.goto('http://127.0.0.1:8000/index.html?hocdiag=1', { waitUntil: 'networkidle' });
const home = await page.evaluate(() => {
  const coarse = matchMedia('(hover:none) and (pointer:coarse)').matches;
  const exterior = getComputedStyle(document.querySelector('.r10-exterior'));
  const copy = document.querySelector('.r10-home-copy').getBoundingClientRect();
  const house = document.querySelector('.r10-house-stage').getBoundingClientRect();
  const build = document.querySelector('meta[name="hoc-build"]')?.content;
  const run13 = [...document.styleSheets].some(s => (s.href || '').includes('hoc-run13-touch.css'));
  const diag = document.querySelector('#hoc-diagnostic-panel')?.textContent || '';
  return { coarse, grid: exterior.gridTemplateColumns, copyBottom: copy.bottom, houseTop: house.top, build, run13, diag };
});
if (!home.coarse) throw new Error('Run 13 test context did not expose coarse/touch pointer; test is invalid');
if (home.build !== 'run13-integrity-20260831a') throw new Error(`Wrong build marker: ${home.build}`);
if (!home.run13) throw new Error('Run 13 touch stylesheet not active');
if (!home.diag.includes('run13-integrity-20260831a') || !home.diag.includes('coarse: true')) throw new Error(`Local diagnostic panel is missing or does not expose required facts: ${home.diag}`);
if (home.grid.trim().split(/\s+/).length !== 1) throw new Error(`Touch homepage is not one-column: ${home.grid}`);
if (home.houseTop < home.copyBottom - 4) throw new Error(`Touch homepage still overlaps side-by-side: copyBottom=${home.copyBottom}, houseTop=${home.houseTop}`);
await page.screenshot({ path: 'qa-artifacts/run13-home-wide-touch-diagnostic.png', fullPage: false });

await page.goto('http://127.0.0.1:8000/catalogue.html', { waitUntil: 'networkidle' });
const desk = await page.evaluate(() => {
  const inner = getComputedStyle(document.querySelector('.r10-frontdesk-inner'));
  const form = getComputedStyle(document.querySelector('.r10-form'));
  return { innerDisplay: inner.display, formColumns: form.gridTemplateColumns };
});
if (desk.innerDisplay !== 'block') throw new Error(`Touch Front Desk did not stack: ${desk.innerDisplay}`);
if (desk.formColumns.trim().split(/\s+/).length !== 1) throw new Error(`Touch form remains multi-column: ${desk.formColumns}`);
await page.locator('#front-desk').scrollIntoViewIfNeeded();
await page.screenshot({ path: 'qa-artifacts/run13-frontdesk-wide-touch.png', fullPage: false });

await browser.close();
console.log('PASS: Run 13 coarse-pointer/wide-viewport plus local diagnostic regression');
