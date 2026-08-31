import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BUILD = 'ce2-run15-20260831a';
const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
await fs.mkdir('qa-artifacts', { recursive: true });

async function assertNoHorizontalOverflow(page, label) {
  const geometry = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
    bodyClient: document.body.clientWidth,
    bodyScroll: document.body.scrollWidth
  }));
  if (geometry.scroll > geometry.client + 1 || geometry.bodyScroll > geometry.bodyClient + 1) {
    throw new Error(`${label}: horizontal overflow ${JSON.stringify(geometry)}`);
  }
}

async function assertBuild(page, label) {
  const build = await page.locator('meta[name="hoc-build"]').getAttribute('content');
  if (build !== BUILD) throw new Error(`${label}: wrong build marker ${build}`);
}

async function assertFocus(page, label) {
  await page.keyboard.press('Tab');
  const focus = await page.evaluate(() => {
    const el = document.activeElement;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return {
      tag: el?.tagName || '',
      text: el?.textContent?.trim() || '',
      outlineStyle: style.outlineStyle,
      outlineWidth: parseFloat(style.outlineWidth || '0'),
      visible: rect.width > 0 && rect.height > 0
    };
  });
  if (!focus.visible || focus.outlineStyle === 'none' || focus.outlineWidth < 2) {
    throw new Error(`${label}: first keyboard focus is not strongly visible: ${JSON.stringify(focus)}`);
  }
}

async function assertFlagship(page, name) {
  const result = await page.evaluate(() => {
    const hero = document.querySelector('.hero-stage');
    const h1 = document.querySelector('.hero-word');
    const ticker = document.querySelector('.ticker');
    const principles = document.querySelectorAll('.principle');
    if (!hero || !h1 || !ticker) return { missing: true };
    const heroStyle = getComputedStyle(hero);
    const h1Style = getComputedStyle(h1);
    const heroRect = hero.getBoundingClientRect();
    return {
      missing: false,
      heroHeight: heroRect.height,
      heroBackground: heroStyle.backgroundImage,
      h1Size: parseFloat(h1Style.fontSize),
      h1LineHeight: parseFloat(h1Style.lineHeight),
      tickerHeight: ticker.getBoundingClientRect().height,
      principles: principles.length,
      oldSilhouette: Boolean(document.querySelector('.hero-silhouette'))
    };
  });
  if (result.missing) throw new Error(`${name}: flagship hero/ticker missing`);
  if (result.heroHeight < 520) throw new Error(`${name}: flagship hero too shallow ${JSON.stringify(result)}`);
  if (!result.heroBackground || result.heroBackground === 'none') throw new Error(`${name}: flagship hero treatment missing`);
  if (result.tickerHeight < 20 || result.principles !== 4) throw new Error(`${name}: House narrative structure incomplete ${JSON.stringify(result)}`);
  if (result.oldSilhouette) throw new Error(`${name}: rejected silhouette layer returned`);
}

async function exercise(viewport, name, options = {}) {
  const context = await browser.newContext({ viewport, ...options });
  const page = await context.newPage();
  const externalRequests = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.hostname !== '127.0.0.1') externalRequests.push(request.url());
  });

  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await assertBuild(page, `${name} home`);
  await assertNoHorizontalOverflow(page, `${name} home`);
  await page.locator('h1').waitFor({ state: 'visible' });
  await assertFlagship(page, name);
  if (await page.locator('#hoc-diagnostic-panel').count()) throw new Error(`${name}: diagnostics visible without opt-in query`);
  await page.screenshot({ path: `qa-artifacts/${name}-home.png`, fullPage: true });
  await assertFocus(page, `${name} home`);

  for (const [path, title] of [
    ['catalogue.html', 'portfolio'],
    ['privacy.html', 'privacy'],
    ['terms.html', 'terms'],
    ['404.html', '404']
  ]) {
    await page.goto(`${BASE}/${path}`, { waitUntil: 'networkidle' });
    await assertBuild(page, `${name} ${title}`);
    await page.locator('h1').waitFor({ state: 'visible' });
    await assertNoHorizontalOverflow(page, `${name} ${title}`);
  }

  await page.goto(`${BASE}/catalogue.html`, { waitUntil: 'networkidle' });
  const rows = await page.locator('.ledger-row').count();
  if (rows !== 4) throw new Error(`${name}: portfolio ledger expected 4 fields, got ${rows}`);
  await page.screenshot({ path: `qa-artifacts/${name}-portfolio.png`, fullPage: true });

  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await assertNoHorizontalOverflow(page, `${name} 200% text`);
  if (!await page.locator('#contact').isVisible()) throw new Error(`${name}: contact section lost at 200% text size`);
  if (!await page.locator('#house').isVisible()) throw new Error(`${name}: House story lost at 200% text size`);

  await page.goto(`${BASE}/index.html?hocdiag=1`, { waitUntil: 'networkidle' });
  const diagnostic = page.locator('#hoc-diagnostic-panel');
  await diagnostic.waitFor({ state: 'visible' });
  const diagText = await diagnostic.textContent();
  if (!diagText?.includes(BUILD) || !diagText.includes('CSS viewport') || !diagText.includes('Pointer coarse')) {
    throw new Error(`${name}: diagnostic mode does not expose required local facts`);
  }

  if (externalRequests.length) {
    throw new Error(`${name}: page made unexpected external requests: ${[...new Set(externalRequests)].join(', ')}`);
  }
  await context.close();
}

await exercise({ width: 1440, height: 900 }, 'desktop');
await exercise({ width: 390, height: 844 }, 'mobile');
await exercise({ width: 320, height: 900 }, 'reflow-320');
await exercise({ width: 800, height: 1280 }, 'wide-mobile', { hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
await exercise({ width: 1200, height: 900 }, 'wide-touch', { hasTouch: true, isMobile: true, deviceScaleFactor: 1 });

await browser.close();
console.log('PASS: Run 15 flagship render, responsive, focus, text enlargement, diagnostics and no-tracking checks');
