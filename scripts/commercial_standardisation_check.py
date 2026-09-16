from pathlib import Path
from html import unescape
from urllib.parse import urlparse
import re

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_PAGES = [
    'catalogue-ai-digital.html',
    'catalogue-operations.html',
    'catalogue-commercial.html',
    'catalogue-learning.html',
    'catalogue-church-parish.html',
    'catalogue-charity-public.html',
    'catalogue-research.html',
]
FORBIDDEN = (
    'synthetic',
    'customer 000',
    's2 / s3 / s4',
    's2 serviceable-internal',
    's3 web-candidate',
    's4 candidate',
    'external proof required',
    'owner gate',
    'internal candidate',
    'internal qa',
    'proprietor-approved',
    'lifecycle status',
    'customers also bought',
    'popular with customers',
    'most customers choose',
    'complete your package',
)
DISCLOSURE = 'Illustrative example — shown to explain how the service can be applied. It is not a customer testimonial or measured result.'
IDENTITY_SRC = 'assets/house-of-carol-identity.webp'
IDENTITY_ALT = 'House of Carol — People, Ideas, Solutions, Real Progress. Intelligence for a kinder, more capable world.'


def fail(message):
    raise SystemExit('FAIL: ' + message)


def plain(fragment):
    fragment = re.sub(r'<[^>]+>', ' ', fragment or '')
    return re.sub(r'\s+', ' ', unescape(fragment)).strip()


routes = {}
for category in CATEGORY_PAGES:
    text = (ROOT / category).read_text(encoding='utf-8')
    for offer_id, href in re.findall(
        r'<article class="service-entry(?: [^"]*)?" id="hoc-\d+" data-offer-id="(HOC-\d{3})">\s*<a class="service-card-link" href="([^"]+)">',
        text,
        re.I,
    ):
        if offer_id in routes:
            fail('duplicate current offer id ' + offer_id)
        routes[offer_id] = href

if len(routes) != 53 or len(set(routes.values())) != 53:
    fail(f'expected 53 unique current DEVELOP routes, found {len(routes)}/{len(set(routes.values()))}')
current = set(routes.values())

for offer_id, href in sorted(routes.items()):
    path = ROOT / href
    if not path.exists():
        fail(f'{offer_id}: missing route {href}')
    text = path.read_text(encoding='utf-8')
    low = text.lower()

    exact_once = {
        'canonical hero': 'class="product-hero standard-product-hero"',
        'What changes': '<h2>What changes</h2>',
        'What you will receive': '<h2>What you will receive</h2>',
        'SEE HOW THIS CAN WORK': '<h2>SEE HOW THIS CAN WORK</h2>',
        'WHERE THIS COULD LEAD NEXT': '<h2>WHERE THIS COULD LEAD NEXT</h2>',
        'A defined engagement': '<h2>A defined engagement</h2>',
        'identity banner': 'class="identity-banner"',
        'disclosure group': 'class="hoc-accordion-group"',
        'final CTA': 'class="shell cta-panel"',
        'context navigation': 'class="service-context-nav"',
    }
    for label, marker in exact_once.items():
        count = text.count(marker)
        if count != 1:
            fail(f'{offer_id} {href}: {label} count {count}, expected 1')

    if text.count(DISCLOSURE) != 1:
        fail(f'{offer_id} {href}: worked-example disclosure count must be 1')
    identity = re.findall(r'<section class="identity-banner"[^>]*>\s*<img\b([^>]*)>', text, re.I | re.S)
    if len(identity) != 1:
        fail(f'{offer_id} {href}: unreadable identity banner')
    attrs = identity[0]
    if f'src="{IDENTITY_SRC}"' not in attrs or f'alt="{IDENTITY_ALT}"' not in attrs:
        fail(f'{offer_id} {href}: identity asset or alt text drift')
    if not re.search(r'\bwidth="1536"', attrs) or not re.search(r'\bheight="1152"', attrs):
        fail(f'{offer_id} {href}: identity dimensions drift')

    for forbidden in FORBIDDEN:
        if forbidden in low:
            fail(f'{offer_id} {href}: forbidden internal/unsupported customer language: {forbidden}')

    order = [
        ('breadcrumbs', 'class="service-breadcrumbs"'),
        ('hero', 'class="product-hero standard-product-hero"'),
        ('what changes', '<h2>What changes</h2>'),
        ('deliverables', '<h2>What you will receive</h2>'),
        ('worked example', '<h2>SEE HOW THIS CAN WORK</h2>'),
        ('next services', '<h2>WHERE THIS COULD LEAD NEXT</h2>'),
        ('defined engagement', '<h2>A defined engagement</h2>'),
        ('identity', 'class="identity-banner"'),
        ('questions', 'class="hoc-accordion-group"'),
        ('final CTA', 'class="shell cta-panel"'),
        ('context nav', 'class="service-context-nav"'),
        ('footer', '<footer class="site-footer">'),
    ]
    positions = [(label, text.find(marker)) for label, marker in order]
    if any(pos < 0 for _, pos in positions):
        fail(f'{offer_id} {href}: module-order marker missing')
    nums = [pos for _, pos in positions]
    if nums != sorted(nums) or len(set(nums)) != len(nums):
        fail(f'{offer_id} {href}: module order invalid')

    next_start = text.find('<h2>WHERE THIS COULD LEAD NEXT</h2>')
    next_section_start = text.rfind('<section', 0, next_start)
    next_section_end = text.find('</section>', next_start)
    if next_section_start < 0 or next_section_end < 0:
        fail(f'{offer_id} {href}: next-service section unreadable')
    next_block = text[next_section_start:next_section_end + len('</section>')]
    recs = re.findall(r'<article class="worked-example-finding">(.*?)</article>', next_block, re.I | re.S)
    if not 1 <= len(recs) <= 3:
        fail(f'{offer_id} {href}: recommendation count {len(recs)}, expected 1-3')
    targets = []
    for card in recs:
        match = re.search(r'<a\s+href="([^"]+)">Explore\s+.*?→</a>', card, re.I | re.S)
        if not match:
            fail(f'{offer_id} {href}: recommendation link pattern missing')
        target = match.group(1)
        targets.append(target)
        if target == href:
            fail(f'{offer_id} {href}: self recommendation')
        if target not in current:
            fail(f'{offer_id} {href}: recommendation target is not a current DEVELOP route: {target}')
        if not re.search(r'<p>If\s+.+?,\s+this can help you\s+.+?\.</p>', card, re.I | re.S):
            fail(f'{offer_id} {href}: recommendation lacks condition/outcome wording')
    if len(targets) != len(set(targets)):
        fail(f'{offer_id} {href}: duplicate recommendation target')
    if 'This service is complete in its own right.' not in next_block:
        fail(f'{offer_id} {href}: independent-completion wording missing')
    if 'no further House of Carol service is needed' not in next_block:
        fail(f'{offer_id} {href}: clean-close condition missing')
    if 'You do not need to choose another service now.' not in next_block:
        fail(f'{offer_id} {href}: restrained closing line missing')

    # Local link and asset existence within each product page.
    for attr, target in re.findall(r'\b(href|src)="([^"]+)"', text, re.I):
        parsed = urlparse(target)
        if parsed.scheme or target.startswith('#') or target.startswith('mailto:') or target.startswith('tel:'):
            continue
        local = parsed.path
        if not local:
            continue
        if not (ROOT / local).exists():
            fail(f'{offer_id} {href}: broken local {attr} {target}')

if list(ROOT.glob('case-study-*.html')) or (ROOT / 'case-studies.html').exists():
    fail('superseded generated 53-case-study layer remains in build workspace')

print('PASS: 53/53 current DEVELOP routes use the locked commercial module order; 53/53 identity banners, worked examples and conditional next-service modules are present exactly once; recommendation targets are current, bounded and non-self; internal language, generated case-study artefacts and broken local links/assets are absent')
