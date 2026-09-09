from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = [
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
]
PRODUCT_PAGES = [
    'process-design-sprint.html',
    'independent-document-review.html',
    'research-briefing.html',
    'shared-drive-cleanup.html',
    'tender-review.html',
]
EXPECTED_NAV = [
    'index.html',
    'how-it-works.html',
    'catalogue.html',
    'about.html',
    'contact.html',
]
REQUIRED_ASSETS = [
    'assets/hoc-rebuild.css',
    'assets/hoc-contact.css',
    'assets/hoc-catalogue.css',
    'assets/hoc-mark.svg',
    'robots.txt',
]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.viewport = False
        self.robots = None
        self.csp = None
        self.titles = 0
        self.h1s = 0
        self.descriptions = []
        self.forms = []
        self.scripts = []
        self.labels = set()
        self.controls = set()
        self.hrefs = []
        self.ids = set()
        self.main_nav_hrefs = []
        self._nav = None

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: (v or '') for k, v in attrs_list}
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'html':
            self.lang = attrs.get('lang')
        elif tag == 'title':
            self.titles += 1
        elif tag == 'h1':
            self.h1s += 1
        elif tag == 'meta':
            if attrs.get('name') == 'viewport':
                self.viewport = bool(attrs.get('content'))
            elif attrs.get('name') == 'robots':
                self.robots = attrs.get('content')
            elif attrs.get('name') == 'description':
                self.descriptions.append(attrs.get('content'))
            elif attrs.get('http-equiv', '').lower() == 'content-security-policy':
                self.csp = attrs.get('content')
        elif tag == 'form':
            self.forms.append(attrs)
        elif tag == 'script':
            self.scripts.append(attrs)
        elif tag == 'label' and attrs.get('for'):
            self.labels.add(attrs['for'])
        elif tag in ('input', 'textarea', 'select') and attrs.get('id') and attrs.get('type') != 'hidden':
            self.controls.add(attrs['id'])
        elif tag == 'nav':
            classes = attrs.get('class', '').split()
            self._nav = 'main' if 'main-nav' in classes else 'other'
        elif tag == 'a' and attrs.get('href'):
            self.hrefs.append(attrs['href'])
            if self._nav == 'main':
                self.main_nav_hrefs.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'nav':
            self._nav = None


def fail(message):
    raise SystemExit(f'FAIL: {message}')


def parsed(page_name):
    parser = Parser()
    parser.feed((ROOT / page_name).read_text(encoding='utf-8'))
    return parser


# 1. Expected public files and assets exist.
for name in PUBLIC_PAGES + REQUIRED_ASSETS:
    if not (ROOT / name).exists():
        fail(f'missing {name}')

parsers = {name: parsed(name) for name in PUBLIC_PAGES}

# 2. Every public page has one title, one H1 and complete baseline metadata.
for name, parser in parsers.items():
    if parser.lang != 'en-GB' or not parser.viewport:
        fail(f'{name}: language or viewport metadata')
    if parser.titles != 1 or parser.h1s != 1 or len(parser.descriptions) != 1:
        fail(f'{name}: title, description or H1 count')

# 3. Containment remains in place on every public page.
for name, parser in parsers.items():
    if parser.robots != 'noindex,nofollow':
        fail(f'{name}: indexing containment')
if 'Disallow: /' not in (ROOT / 'robots.txt').read_text(encoding='utf-8'):
    fail('robots.txt containment')

# 4. CSP and no-script baseline hold.
for name, parser in parsers.items():
    if not parser.csp or any(
        directive not in parser.csp
        for directive in ("object-src 'none'", "base-uri 'self'", "script-src 'none'", "connect-src 'none'")
    ):
        fail(f'{name}: CSP')
    if parser.scripts:
        fail(f'{name}: scripts present')

# 5. Main navigation is the same five real pages everywhere, with no section anchors.
for name, parser in parsers.items():
    if parser.main_nav_hrefs != EXPECTED_NAV:
        fail(f'{name}: main navigation {parser.main_nav_hrefs}')
    if any('#' in href for href in parser.main_nav_hrefs):
        fail(f'{name}: section anchor in main navigation')

# 6. Local links resolve, including fragment targets.
for name, parser in parsers.items():
    for href in parser.hrefs:
        url = urlparse(href)
        if url.scheme in ('mailto', 'tel', 'https'):
            continue
        target_name = url.path or name
        target = ROOT / target_name
        if not target.exists():
            fail(f'{name}: broken link {href}')
        if url.fragment:
            target_parser = parsers.get(target_name)
            if target_parser is None and target.suffix == '.html':
                target_parser = parsed(target_name)
            if target_parser is not None and url.fragment not in target_parser.ids:
                fail(f'{name}: missing fragment target {href}')

# 7. The catalogue links every customer-facing product page exactly once.
catalogue = parsers['catalogue.html']
for product in PRODUCT_PAGES:
    if catalogue.hrefs.count(product) != 1:
        fail(f'catalogue: expected one link to {product}')
for internal_variant in ('brandlab-advisory.html', 'brandlab-bureau.html', 'brandlab-signal.html', 'brandlab-studio.html', 'brandlab-works.html'):
    if any(internal_variant in parsers[name].hrefs for name in PUBLIC_PAGES):
        fail(f'public site links internal variant {internal_variant}')

# 8. The approved contact form remains only on Contact, with labelled controls.
all_forms = [(name, form) for name, parser in parsers.items() for form in parser.forms]
if len(all_forms) != 1 or all_forms[0][0] != 'contact.html':
    fail(f'contact form location/count {all_forms}')
contact = parsers['contact.html']
form = contact.forms[0]
if form.get('action') != 'https://formspree.io/f/mgvgrgvb' or form.get('method', '').lower() != 'post':
    fail('contact: approved contact route')
if contact.controls - contact.labels or contact.controls != {'name', 'email', 'message'}:
    fail('contact: labelled controls')

# 9. Required proposition and product truth are present without unsupported marketing claims.
home = (ROOT / 'index.html').read_text(encoding='utf-8').lower()
for text in (
    'a useful place for difficult business work.',
    'five real service pages',
    'bring us a problem',
    'house of carol was founded by alan w gallagher in bristol',
):
    if text not in home:
        fail(f'home missing {text}')
catalogue_text = (ROOT / 'catalogue.html').read_text(encoding='utf-8').lower()
for text in (
    'one-process improvement sprint',
    'independent document review',
    'research briefing',
    'shared drive &amp; document cleanup',
    'tender decision &amp; submission review',
):
    if text not in catalogue_text:
        fail(f'catalogue missing {text}')
all_public_text = '\n'.join((ROOT / name).read_text(encoding='utf-8').lower() for name in PUBLIC_PAGES)
for claim in ('industry-leading', 'world-class', '52 departments', 'customer 000'):
    if claim in all_public_text:
        fail(f'unsupported/internal claim {claim}')

# 10. Legal disclosures remain complete.
privacy = ' '.join((ROOT / 'privacy.html').read_text(encoding='utf-8').lower().split())
for text in ('data controller', 'legitimate interests', 'formspree', 'united states', 'standard contractual clauses', 'information commissioner', 'cookies and analytics'):
    if text not in privacy:
        fail(f'privacy missing {text}')
terms = ' '.join((ROOT / 'terms.html').read_text(encoding='utf-8').lower().split())
for text in ('no automatic offer', 'intellectual property', 'nothing in these terms excludes', 'law of england and wales'):
    if text not in terms:
        fail(f'terms missing {text}')

print('PASS: 10 static checks — files, metadata, containment, CSP, page navigation, links, full catalogue, contact route, proposition truth and legal pages')
