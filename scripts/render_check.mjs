import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const base = 'http://127.0.0.1:8000';
const out = 'qa-artifacts';
await fs.mkdir(out, { recursive: true });

async function assertWithinViewport(page, selectors, name) {
  const failures = await page.evaluate((selectorList) => {
    const viewportWidth = document.documentElement.clientWidth;
    return selectorList.flatMap((selector) => [...document.querySelectorAll(selector)].map((el) => {
      const rect = el.getBoundingClientRect();
      const left = Math.round(rect.left * 10) / 10;
      const right = Math.round(rect.right * 10) / 10;
      return (left < -1 || right > viewportWidth + 1) ? `${selector}: ${left}..${right} / ${viewportWidth}` : null;
    }).filter(Boolean));
  }, selectors);
  if (failures.length) throw new Error(`${name}: content escapes viewport: ${failures.join('; ')}`);
}

async function assertNoHorizontalOverflow(page, name) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (overflow) throw new Error(`${name}: horizontal overflow`);
}

async function exercise(viewport, name, deviceScaleFactor = 1) {
  const compact = name === 'mobile' || name === 'wide-mobile';
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport, deviceScaleFactor, reducedMotion: 'no-preference' });
  const page = await context.newPage();

  await page.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(520);
  await assertNoHorizontalOverflow(page, `${name} homepage`);
  await assertWithinViewport(page, ['.r10-header', '.r10-home-copy', '.r10-home-copy h1', '.r10-lede', '.r10-enter', '.r10-house-stage'], `${name} homepage`);

  const firstFold = await page.evaluate(() => {
    const house = document.querySelector('.r10-house')?.getBoundingClientRect();
    const cta = document.querySelector('.r10-enter')?.getBoundingClientRect();
    const lit = document.querySelectorAll('[data-facade-room].is-home-lit').length;
    return { viewport: window.innerHeight, houseTop: house?.top ?? 9999, houseBottom: house?.bottom ?? 9999, houseWidth: house?.width ?? 0, ctaTop: cta?.top ?? 9999, lit };
  });
  if (firstFold.houseTop > firstFold.viewport * 0.94) throw new Error(`${name}: House does not meaningfully enter the first viewport`);
  if (compact && firstFold.houseWidth < viewport.width * 0.70) throw new Error(`${name}: House is visually too small for a compact/touch viewport`);
  if (firstFold.ctaTop > firstFold.viewport * 0.90) throw new Error(`${name}: entry action falls out of the first viewport`);
  if (firstFold.lit < 2) throw new Error(`${name}: first impression lacks the intended lived-in House signal`);
  await page.screenshot({ path: `${out}/home-${name}.png`, fullPage: false });

  const businessHotspot = page.locator('[data-room-hotspot="business"]');
  await businessHotspot.dispatchEvent('mouseenter');
  const roomActive = await page.locator('[data-facade-room="business"]').evaluate((el) => el.classList.contains('is-active'));
  if (!roomActive) throw new Error(`${name}: facade room interaction did not activate`);
  const readout = await page.locator('[data-house-readout] strong').textContent();
  if (!readout?.includes('hard thing simpler')) throw new Error(`${name}: room interaction did not provide meaningful feedback`);

  const door = page.locator('[data-enter-house]').first();
  await door.dispatchEvent('mouseenter');
  const doorOpen = await page.locator('[data-house-stage]').evaluate((el) => el.classList.contains('is-door-open'));
  if (!doorOpen) throw new Error(`${name}: door interaction did not activate`);
  await page.screenshot({ path: `${out}/home-interaction-${name}.png`, fullPage: false });

  await page.goto(`${base}/catalogue.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(320);
  await assertNoHorizontalOverflow(page, `${name} catalogue`);
  await assertWithinViewport(page, ['.r10-rooms-intro', '.r10-rooms-intro h1', '.r10-room-theatre', '.r10-plan-zone', '.r10-room-display'], `${name} catalogue`);

  if (compact) {
    const planPosition = await page.locator('.r10-plan-shell').evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return { top: rect.top, viewport: window.innerHeight };
    });
    if (planPosition.top > planPosition.viewport * 1.28) throw new Error(`${name} catalogue: visitor waits too long before reaching the interactive plan`);
  }
  await page.screenshot({ path: `${out}/catalogue-${name}.png`, fullPage: false });

  await page.locator('[data-plan-room="publishing"]').click();
  await page.waitForTimeout(420);
  const publishingActive = await page.locator('[data-plan-art="publishing"]').evaluate((el) => el.classList.contains('is-current'));
  const publishingVisible = await page.locator('[data-room-panel="publishing"]').evaluate((el) => el.classList.contains('is-current') && getComputedStyle(el).display !== 'none');
  const oldPanelHidden = await page.locator('[data-room-panel="business"]').evaluate((el) => getComputedStyle(el).display === 'none');
  const theme = await page.locator('body').getAttribute('data-room-theme');
  if (!publishingActive || !publishingVisible || !oldPanelHidden || theme !== 'publishing') throw new Error(`${name}: room theatre did not switch coherently`);
  if (compact) {
    const roomPosition = await page.locator('.r10-room-display').evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return { top: rect.top, bottom: rect.bottom, viewport: window.innerHeight };
    });
    if (roomPosition.top > 100 || roomPosition.bottom < 240) throw new Error(`${name} catalogue: selected room was not brought into a useful viewing position`);
  }
  await page.screenshot({ path: `${out}/catalogue-publishing-${name}.png`, fullPage: false });

  await page.locator('[data-room-index="other"]').click();
  await page.waitForTimeout(360);
  const otherVisible = await page.locator('[data-room-panel="other"]').evaluate((el) => el.classList.contains('is-current') && getComputedStyle(el).display !== 'none');
  if (!otherVisible) throw new Error(`${name}: room index did not switch the theatre`);

  await page.locator('#front-desk').scrollIntoViewIfNeeded();
  await page.waitForTimeout(140);
  await assertWithinViewport(page, ['.r10-frontdesk-inner', '.r10-desk-copy', '.r10-form'], `${name} front desk`);
  if (compact) {
    const frontDesk = await page.evaluate(() => {
      const inner = document.querySelector('.r10-frontdesk-inner');
      const form = document.querySelector('.r10-form');
      const actions = document.querySelector('.r10-form-actions');
      return {
        innerDisplay: inner ? getComputedStyle(inner).display : '',
        formColumns: form ? getComputedStyle(form).gridTemplateColumns.split(' ').filter(Boolean).length : 99,
        actionsDisplay: actions ? getComputedStyle(actions).display : ''
      };
    });
    if (frontDesk.innerDisplay !== 'block') throw new Error(`${name} front desk: compact layout did not stack`);
    if (frontDesk.formColumns !== 1) throw new Error(`${name} front desk: form remains multi-column`);
    if (frontDesk.actionsDisplay !== 'block') throw new Error(`${name} front desk: actions remain desktop side-by-side`);
  }
  await page.screenshot({ path: `${out}/front-desk-${name}.png`, fullPage: false });

  for (const legal of ['privacy', 'terms']) {
    await page.goto(`${base}/${legal}.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(180);
    await assertNoHorizontalOverflow(page, `${name} ${legal}`);
    await assertWithinViewport(page, ['.r10-header', '.r10-legal-main', '.r10-legal-main h1', '.r10-footer-inner'], `${name} ${legal}`);
    await page.screenshot({ path: `${out}/${legal}-${name}.png`, fullPage: false });
  }

  await page.goto(`${base}/404.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(180);
  await assertNoHorizontalOverflow(page, `${name} 404`);
  await assertWithinViewport(page, ['.r10-header', '.r10-error-copy', '.r10-error h1', '.r10-error-actions'], `${name} 404`);
  await page.screenshot({ path: `${out}/404-${name}.png`, fullPage: false });

  await browser.close();
}

await exercise({ width: 1440, height: 900 }, 'desktop');
await exercise({ width: 800, height: 1280 }, 'wide-mobile', 1);
await exercise({ width: 390, height: 844 }, 'mobile', 2);

const reducedBrowser = await chromium.launch({ headless: true });
const reducedContext = await reducedBrowser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
const reducedPage = await reducedContext.newPage();
await reducedPage.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
await reducedPage.locator('[data-enter-house]').first().focus({ preventScroll: true });
const transition = await reducedPage.locator('.r10-door-leaf').evaluate((el) => getComputedStyle(el).transitionDuration);
if (transition !== '0s') throw new Error(`reduced-motion: expected no door transition, got ${transition}`);
await reducedPage.goto(`${base}/catalogue.html`, { waitUntil: 'networkidle' });
await reducedPage.locator('[data-room-index="publishing"]').click();
await reducedPage.waitForTimeout(40);
const scrollBehaviour = await reducedPage.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior);
if (scrollBehaviour === 'smooth') throw new Error('reduced-motion: smooth scrolling remains active');
await reducedBrowser.close();

console.log('PASS: Run 12 whole-House browser interaction, narrow + Samsung-class wide-mobile, responsive, viewport-bounds and reduced-motion checks');
