import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
await fs.mkdir('qa-artifacts', { recursive: true });

async function noOverflow(page, label) {
  const geometry = await page.evaluate(() => {
    const clientWidth = document.documentElement.clientWidth;
    const scrollWidth = document.documentElement.scrollWidth;
    const offenders = [...document.querySelectorAll('*')]
      .map((el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return {
          tag: el.tagName,
          id: el.id || '',
          cls: typeof el.className === 'string' ? el.className : '',
          left: Math.round(r.left * 100) / 100,
          right: Math.round(r.right * 100) / 100,
          width: Math.round(r.width * 100) / 100,
          position: s.position,
          overflowX: s.overflowX,
          text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90),
        };
      })
      .filter((x) => x.right > clientWidth + 1 || x.left < -1)
      .sort((a, b) => Math.max(b.right - clientWidth, -b.left) - Math.max(a.right - clientWidth, -a.left))
      .slice(0, 12);
    return { clientWidth, scrollWidth, offenders };
  });
  if (geometry.scrollWidth > geometry.clientWidth + 1) {
    throw new Error(`${label}: overflow ${JSON.stringify(geometry)}`);
  }
}

async function visibleText(page) {
  return (await page.locator('body').innerText()).toLowerCase();
}

async function checkCurrentHome(page, name) {
  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.locator('h1').waitFor();
  const body = await visibleText(page);
  for (const text of [
    'a useful place for difficult business work.',
    'what can the house help with?',
    'products & services',
    'bring us a problem',
    'contact',
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
  const body = await visibleText(page);
  for (const text of [
    'a fresh pair of eyes before an important submission goes in.',
    'fit first. files later.',
    'read what was asked',
    'test what is claimed',
    'find what was missed',
    'prioritise what matters',
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
