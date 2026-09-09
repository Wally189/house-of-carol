import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
await fs.mkdir('qa-artifacts', { recursive: true });

const PUBLIC_PAGES = [
  'index.html',
  'how-it-works.html',
  'catalogue.html',
  'about.html',
  'contact.html',
  'process-design-sprint.html',
  'independent-document-review.html',
  'research-briefing.html',
  'shared-drive-cleanup.html',
  'tender-review.html',
  'privacy.html',
  'terms.html',
  '404.html',
];
const EXPECTED_NAV = [
  'index.html',
  'how-it-works.html',
  'catalogue.html',
  'about.html',
  'contact.html',
];
const PRODUCT_PAGES = [
  'process-design-sprint.html',
  'independent-document-review.html',
  'research-briefing.html',
  'shared-drive-cleanup.html',
  'tender-review.html',
];

async function noOverflow(page, label) {
  const geometry = await page.evaluate(() => {
    const clientWidth = document.documentElement.clientWidth;
    const offenders = [...document.querySelectorAll('*')]
      .map((el) => {
        const rect = el.getBoundingClientRect();
        return {
          tag: el.tagName,
          id: el.id || '',
          cls: typeof el.className === 'string' ? el.className : '',
          left: Math.round(rect.left * 100) / 100,
          right: Math.round(rect.right * 100) / 100,
          width: Math.round(rect.width * 100) / 100,
          text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90),
        };
      })
      .filter((item) => item.right > clientWidth + 1 || item.left < -1)
      .slice(0, 12);
    return { clientWidth, offenders };
  });
  if (geometry.offenders.length) {
    throw new Error(label + ': visible overflow ' + JSON.stringify(geometry));
  }
}

async function checkPage(page, path, label) {
  const response = await page.goto(BASE + '/' + path, { waitUntil: 'networkidle' });
  if (!response || !response.ok()) throw new Error(label + ': HTTP ' + response?.status());
  if (await page.locator('h1').count() !== 1) throw new Error(label + ': H1 count');
  const navHrefs = await page.locator('.main-nav a').evaluateAll((links) => links.map((a) => a.getAttribute('href')));
  if (JSON.stringify(navHrefs) !== JSON.stringify(EXPECTED_NAV)) {
    throw new Error(label + ': main navigation ' + JSON.stringify(navHrefs));
  }
  if (navHrefs.some((href) => href.includes('#'))) throw new Error(label + ': section anchor in main navigation');
  await noOverflow(page, label);
  await page.evaluate(() => { document.body.style.fontSize = '200%'; });
  await noOverflow(page, label + ' 200% text');
}

async function checkJourney(page, name) {
  await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
  for (const [href, expectedPath] of [
    ['how-it-works.html', '/how-it-works.html'],
    ['catalogue.html', '/catalogue.html'],
    ['about.html', '/about.html'],
    ['contact.html', '/contact.html'],
  ]) {
    await page.locator('.main-nav a[href="' + href + '"]').click();
    if (new URL(page.url()).pathname !== expectedPath) {
      throw new Error(name + ': ' + href + ' did not open its own page');
    }
    await page.goBack({ waitUntil: 'networkidle' });
  }

  await page.goto(BASE + '/catalogue.html', { waitUntil: 'networkidle' });
  const productHrefs = await page.locator('.catalogue-card a.button').evaluateAll((links) => links.map((a) => a.getAttribute('href')));
  if (JSON.stringify(productHrefs.sort()) !== JSON.stringify([...PRODUCT_PAGES].sort())) {
    throw new Error(name + ': catalogue products ' + JSON.stringify(productHrefs));
  }

  await page.goto(BASE + '/contact.html', { waitUntil: 'networkidle' });
  if (await page.locator('form').count() !== 1) throw new Error(name + ': contact form count');
  const form = page.locator('form');
  if (await form.getAttribute('action') !== 'https://formspree.io/f/mgvgrgvb') throw new Error(name + ': contact action');
  for (const id of ['name', 'email', 'message']) {
    if (!await page.locator('#' + id).isVisible()) throw new Error(name + ': contact control ' + id);
  }
}

async function run(viewport, name) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  for (const path of PUBLIC_PAGES) {
    await checkPage(page, path, name + ' ' + path);
  }
  await checkJourney(page, name);
  for (const path of ['index.html', 'catalogue.html', 'contact.html']) {
    await page.goto(BASE + '/' + path, { waitUntil: 'networkidle' });
    await page.screenshot({ path: 'qa-artifacts/' + name + '-' + path.replace('.html', '') + '.png', fullPage: true });
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
console.log('PASS: multipage navigation, five-product catalogue, contact route, desktop/tablet/mobile rendering and 200% text reflow');
