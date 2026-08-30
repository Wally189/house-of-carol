import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const base = 'http://127.0.0.1:8000';
const out = 'qa-artifacts';
await fs.mkdir(out, { recursive: true });

async function exercise(viewport, name, deviceScaleFactor = 1) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport, deviceScaleFactor, reducedMotion: 'no-preference' });
  const page = await context.newPage();

  await page.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  const homeOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (homeOverflow) throw new Error(`${name}: horizontal overflow on homepage`);
  await page.screenshot({ path: `${out}/home-${name}.png`, fullPage: true });

  const businessHotspot = page.locator('[data-room-hotspot="business"]');
  await businessHotspot.dispatchEvent('mouseenter');
  const roomActive = await page.locator('[data-facade-room="business"]').evaluate((el) => el.classList.contains('is-active'));
  if (!roomActive) throw new Error(`${name}: facade room interaction did not activate`);

  const door = page.locator('[data-enter-house]').last();
  await door.dispatchEvent('mouseenter');
  const doorOpen = await page.locator('[data-house-stage]').evaluate((el) => el.classList.contains('is-door-open'));
  if (!doorOpen) throw new Error(`${name}: door interaction did not activate`);
  await page.screenshot({ path: `${out}/home-interaction-${name}.png`, fullPage: false });

  await page.goto(`${base}/catalogue.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(220);
  const catalogueOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (catalogueOverflow) throw new Error(`${name}: horizontal overflow on catalogue`);
  await page.screenshot({ path: `${out}/catalogue-top-${name}.png`, fullPage: false });

  const publishing = page.locator('[data-plan-room="publishing"]');
  await publishing.dispatchEvent('mouseenter');
  const publishingActive = await publishing.evaluate((el) => el.classList.contains('is-current'));
  const artActive = await page.locator('[data-plan-art="publishing"]').evaluate((el) => el.classList.contains('is-current'));
  if (!publishingActive || !artActive) throw new Error(`${name}: floor-plan interaction did not activate both hit area and plan art`);

  for (const selector of ['#business', '#products', '#publishing', '#other']) {
    await page.locator(selector).scrollIntoViewIfNeeded();
    await page.waitForTimeout(90);
  }

  await page.locator('#business').scrollIntoViewIfNeeded();
  await page.waitForTimeout(80);
  await page.screenshot({ path: `${out}/room-business-${name}.png`, fullPage: false });

  await page.locator('#publishing').scrollIntoViewIfNeeded();
  await page.waitForTimeout(80);
  await page.screenshot({ path: `${out}/room-publishing-${name}.png`, fullPage: false });

  await page.locator('#front-desk').scrollIntoViewIfNeeded();
  await page.waitForTimeout(80);
  await page.screenshot({ path: `${out}/front-desk-${name}.png`, fullPage: false });

  await browser.close();
}

await exercise({ width: 1440, height: 900 }, 'desktop');
await exercise({ width: 390, height: 844 }, 'mobile', 2);

const reducedBrowser = await chromium.launch({ headless: true });
const reducedContext = await reducedBrowser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
const reducedPage = await reducedContext.newPage();
await reducedPage.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
await reducedPage.locator('[data-enter-house]').last().focus({ preventScroll: true });
const transition = await reducedPage.locator('.door-leaf').evaluate((el) => getComputedStyle(el).transitionDuration);
if (transition !== '0s') throw new Error(`reduced-motion: expected no door transition, got ${transition}`);
await reducedBrowser.close();

console.log('PASS: browser interaction, responsive and reduced-motion checks');
