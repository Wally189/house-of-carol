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
  if (geometry.offenders.length) {
    throw new Error(`${label}: visible overflow ${JSON.stringify(geometry)}`);
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
    'where we help',
    'products & services',
    'browse the house of carol catalogue.',
    'bring us a problem',
  ]) {
    if (!body.includes(text)) throw new Error(`${name}: missing ${text}`);
  }
  if (await page.locator('form').count() !== 1) throw new Error(`${name}: contact form count`);
  for (const id of ['name', 'email', 'message']) {
    if (!await page.locator(`#${id}`).isVisible()) throw new Error(`${name}: missing ${id}`);
  }
  if (await page.locator('a[href="process-design-sprint.html"]').count() !== 0) throw new Error(`${name}: home bypasses Catalogue`);
  if (await page.locator('a[href="catalogue.html"]').count() < 1) throw new Error(`${name}: Catalogue route missing`);
  await noOverflow(page, name);
  await page.screenshot({ path: `qa-artifacts/${name}-home.png`, fullPage: true });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await noOverflow(page, `${name} home 200%`);
}

async function checkCatalogue(page, name) {
  await page.goto(`${BASE}/catalogue.html`, { waitUntil: 'networkidle' });
  await page.locator('h1').waitFor();
  const body = await visibleText(page);
  for (const text of [
    'useful work, with a clear boundary.',
    'one important business process, properly sorted out.',
    '£1,500',
    'not yet released as a fixed offer',
  ]) {
    if (!body.includes(text)) throw new Error(`${name} catalogue: missing ${text}`);
  }
  if (await page.locator('a[href="process-design-sprint.html"]').count() !== 1) throw new Error(`${name}: Catalogue HOC-015 route count`);
  await noOverflow(page, `${name} catalogue`);
  await page.screenshot({ path: `qa-artifacts/${name}-catalogue.png`, fullPage: true });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await noOverflow(page, `${name} catalogue 200%`);
}

async function checkProduct(page, name) {
  await page.goto(`${BASE}/process-design-sprint.html`, { waitUntil: 'networkidle' });
  await page.locator('h1').waitFor();
  const body = await visibleText(page);
  for (const text of [
    "your business shouldn't depend on one person remembering how everything works.",
    '£1,500',
    'before and after should be obvious.',
    'worth buying only when the problem is real.',
    'a real person accountable for the result.',
  ]) {
    if (!body.includes(text)) throw new Error(`${name} HOC-015: missing ${text}`);
  }
  if (await page.locator('a[href="catalogue.html"]').count() < 1) throw new Error(`${name}: HOC-015 Catalogue return missing`);
  await noOverflow(page, `${name} HOC-015`);
  await page.screenshot({ path: `qa-artifacts/${name}-hoc015.png`, fullPage: true });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await noOverflow(page, `${name} HOC-015 200%`);
}

async function run(viewport, name) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  await checkCurrentHome(page, name);
  await checkCatalogue(page, name);
  await checkProduct(page, name);
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
console.log('PASS: current home, Catalogue and HOC-015 journey render across desktop, tablet, mobile, 320px reflow and 200% text');
