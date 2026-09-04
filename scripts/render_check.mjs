import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
await fs.mkdir('qa-artifacts', { recursive: true });

async function noOverflow(page, label) {
  const geometry = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  if (geometry.scrollWidth > geometry.clientWidth + 1) {
    throw new Error(`${label}: overflow ${JSON.stringify(geometry)}`);
  }
}

async function checkCurrentHome(page, name) {
  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.locator('h1').waitFor();
  const body = await page.locator('body').innerText();
  for (const text of [
    'A useful place for difficult business work.',
    'What can the House help with?',
    'Products & services',
    'Bring us a problem',
    'Contact',
  ]) {
    if (!body.includes(text)) throw new Error(`${name}: missing ${text}`);
  }
  if (await page.locator('form').count() !== 1) throw new Error(`${name}: contact form count`);
  for (const id of ['name', 'email', 'message']) {
    if (!await page.locator(`#${id}`).isVisible()) throw new Error(`${name}: missing ${id}`);
  }
  await noOverflow(page, name);
  await page.screenshot({ path: `qa-artifacts/${name}-home.png`, fullPage: true });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await noOverflow(page, `${name} 200%`);
}

async function checkTenderReview(page, name) {
  await page.goto(`${BASE}/tender-review.html`, { waitUntil: 'networkidle' });
  await page.locator('h1').waitFor();
  const body = await page.locator('body').innerText();
  for (const text of [
    'A fresh pair of eyes before an important submission goes in.',
    'Fit first. Files later.',
    'Read what was asked',
    'Test what is claimed',
    'Find what was missed',
    'Prioritise what matters',
  ]) {
    if (!body.includes(text)) throw new Error(`${name} tender-review: missing ${text}`);
  }
  await noOverflow(page, `${name} tender-review`);
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await noOverflow(page, `${name} tender-review 200%`);
}

async function run(viewport, name) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  await checkCurrentHome(page, name);
  await checkTenderReview(page, name);
  for (const path of ['privacy.html', 'terms.html']) {
    await page.goto(`${BASE}/${path}`);
    await page.locator('h1').waitFor();
    await noOverflow(page, `${name} ${path}`);
  }
  await context.close();
}

for (const [viewport, name] of [
  [{ width: 1440, height: 900 }, 'desktop'],
  [{ width: 800, height: 1280 }, 'tablet'],
  [{ width: 390, height: 844 }, 'mobile'],
  [{ width: 320, height: 900 }, 'reflow-320'],
]) {
  await run(viewport, name);
}

await browser.close();
console.log('PASS: current home, Tender Review and legal journey render across desktop, tablet, mobile and 200% text');
