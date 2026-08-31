import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BUILD = 'run14-silhouette-20260831a';
const BASE = 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
await fs.mkdir('qa-artifacts', { recursive: true });

async function assertNoHorizontalOverflow(page, label) {
  const geometry = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth
  }));
  if (geometry.scrollWidth > geometry.clientWidth + 1) {
    throw new Error(`${label}: horizontal overflow ${geometry.scrollWidth} > ${geometry.clientWidth}`);
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
  const silhouette = await page.locator('.hero-silhouette').evaluate(el => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return { width: rect.width, height: rect.height, opacity: parseFloat(style.opacity) };
  });
  if (silhouette.width < 120 || silhouette.height < 100 || silhouette.opacity < 0.025 || silhouette.opacity > 0.09) {
    throw new Error(`${name}: silhouette is missing, dominant or effectively invisible: ${JSON.stringify(silhouette)}`);
  }
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

  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await assertNoHorizontalOverflow(page, `${name} 200% text`);
  if (!await page.locator('#contact').isVisible()) throw new Error(`${name}: contact section lost at 200% text size`);

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
console.log('PASS: Run 14 desktop/mobile/320-reflow/wide-touch render, focus, text enlargement, diagnostics and no-tracking checks');
