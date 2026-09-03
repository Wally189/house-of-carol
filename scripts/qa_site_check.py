from pathlib import Path

ROOT = Path('qa')
html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'styles.css').read_text(encoding='utf-8')
low = html.lower()

required = [
    '<html lang="en-GB">'.lower(),
    'noindex,nofollow,noarchive',
    'HOUSE OF CAROL',
    'Tender Decision &amp; Submission Review',
    'Important business work, given proper attention.',
    'QA PREVIEW · NOT OPEN FOR ORDERS',
    'Alan W Gallagher trading as House of Carol',
]
for item in required:
    if item.lower() not in low:
        raise SystemExit(f'FAIL qa storefront missing: {item}')

for forbidden in [
    'alanwgallagher1@gmail.com',
    '0117 970 9545',
    'knole park',
    'guaranteed win',
    'award-winning',
    'market-leading',
    'trusted by',
    '<form',
    'formspree',
    'mailto:',
    'tel:',
    '£495',
    'managed b2b credit control',
]:
    if forbidden.lower() in low:
        raise SystemExit(f'FAIL qa storefront forbidden release item: {forbidden}')

if 'styles.css' not in html:
    raise SystemExit('FAIL qa storefront stylesheet not linked')
if '#081D2D'.lower() not in css.lower() or '#7A1E2E'.lower() not in css.lower():
    raise SystemExit('FAIL qa storefront missing core brand palette')
print('PASS: QA storefront is contained, non-indexed, brand-aligned and free of private/release-only data')
