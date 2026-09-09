from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    'index.html',
    'catalogue.html',
    'process-design-sprint.html',
    'tender-review.html',
    'privacy.html',
    'terms.html',
    '404.html',
)
HTML = [ROOT / n for n in NAMES]
NORMAL_ENTRY_NAMES = (
    'index.html',
    'about.html',
    'tender-review.html',
    'privacy.html',
    'terms.html',
    '404.html',
)

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

    def handle_starttag(self, tag, attrs_list):
        a = {k: (v or '') for k, v in attrs_list}
        if tag == 'html': self.lang = a.get('lang')
        elif tag == 'title': self.titles += 1
        elif tag == 'h1': self.h1s += 1
        elif tag == 'meta':
            if a.get('name') == 'viewport': self.viewport = bool(a.get('content'))
            elif a.get('name') == 'robots': self.robots = a.get('content')
            elif a.get('name') == 'description': self.descriptions.append(a.get('content'))
            elif a.get('http-equiv', '').lower() == 'content-security-policy': self.csp = a.get('content')
        elif tag == 'form': self.forms.append(a)
        elif tag == 'script': self.scripts.append(a)
        elif tag == 'label' and a.get('for'): self.labels.add(a['for'])
        elif tag in ('input', 'textarea', 'select') and a.get('id') and a.get('type') != 'hidden': self.controls.add(a['id'])
        elif tag == 'a' and a.get('href'): self.hrefs.append(a['href'])

def fail(message): raise SystemExit(f'FAIL: {message}')

required_files = [
    *HTML,
    ROOT/'about.html',
    ROOT/'assets/hoc-rebuild.css',
    ROOT/'assets/hoc-contact.css',
    ROOT/'assets/hoc-catalogue-base.css',
    ROOT/'assets/hoc-catalogue-contact.css',
    ROOT/'assets/hoc-catalogue.css',
    ROOT/'assets/hoc-mark.svg',
    ROOT/'robots.txt',
]
for item in required_files:
    if not item.exists(): fail(f'missing {item.relative_to(ROOT)}')

for page in HTML:
    p=Parser(); p.feed(page.read_text(encoding='utf-8'))
    if p.lang!='en-GB' or not p.viewport or p.titles!=1 or p.h1s!=1 or len(p.descriptions)!=1: fail(f'{page.name}: metadata')
    if p.robots!='noindex,nofollow': fail(f'{page.name}: containment')
    if not p.csp or any(x not in p.csp for x in ("object-src 'none'","base-uri 'self'","script-src 'none'")): fail(f'{page.name}: CSP')
    if p.scripts: fail(f'{page.name}: scripts')
    if p.controls-p.labels: fail(f'{page.name}: unlabelled controls')
    for href in p.hrefs:
        u=urlparse(href)
        if u.scheme in ('mailto','tel','https'): continue
        if not (ROOT/(u.path or page.name)).resolve().exists(): fail(f'{page.name}: broken link {href}')

home=(ROOT/'index.html').read_text(encoding='utf-8').lower(); hp=Parser(); hp.feed(home)
if len(hp.forms)!=1 or hp.forms[0].get('action')!='https://formspree.io/f/mgvgrgvb' or hp.forms[0].get('method','').lower()!='post': fail('home: approved contact route')
for x in ('a useful place for difficult business work.','where we help','products &amp; services','browse the house of carol catalogue.','bring us a problem','house of carol was founded by alan w gallagher in bristol'):
    if x not in home: fail(f'home missing {x}')
if 'tender-review.html' in home: fail('home: stale Tender Review route remains')
if 'process-design-sprint.html' in hp.hrefs: fail('home: direct HOC-015 route bypasses Catalogue')
if 'catalogue.html' not in hp.hrefs: fail('home: Catalogue route missing')

catalogue=(ROOT/'catalogue.html').read_text(encoding='utf-8').lower(); cp=Parser(); cp.feed(catalogue)
for x in ('useful work, with a clear boundary.','one important business process, properly sorted out.','£1,500','not yet released as a fixed offer'):
    if x not in catalogue: fail(f'catalogue missing {x}')
if cp.hrefs.count('process-design-sprint.html') != 1: fail('catalogue: expected exactly one released HOC-015 product link')
if 'assets/hoc-catalogue-base.css' not in catalogue: fail('catalogue: isolated approved base stylesheet missing')

product=(ROOT/'process-design-sprint.html').read_text(encoding='utf-8').lower(); pp=Parser(); pp.feed(product)
for x in ("your business shouldn't depend on one person remembering how everything works.",'£1,500','before and after should be obvious.','what we need from you','worth buying only when the problem is real.','a real person accountable for the result.','alan w gallagher'):
    if x not in product: fail(f'HOC-015 page missing {x}')
if 'catalogue.html' not in pp.hrefs: fail('HOC-015: Catalogue return route missing')
if 'assets/hoc-catalogue-base.css' not in product or 'assets/hoc-catalogue-contact.css' not in product: fail('HOC-015: isolated approved stylesheet route missing')

for name in NORMAL_ENTRY_NAMES:
    p=Parser(); p.feed((ROOT/name).read_text(encoding='utf-8'))
    if 'process-design-sprint.html' in p.hrefs:
        fail(f'{name}: direct HOC-015 route bypasses Catalogue')

for text, label in ((home, 'home'), (catalogue, 'catalogue'), (product, 'HOC-015')):
    for forbidden in ('ai-powered','industry-leading','world-class','52 departments','customer 000','trusted by','guaranteed savings'):
        if forbidden in text: fail(f'{label}: unsupported/internal item {forbidden}')

privacy=' '.join((ROOT/'privacy.html').read_text(encoding='utf-8').lower().split())
for x in ('data controller','legitimate interests','formspree','united states','standard contractual clauses','information commissioner','cookies and analytics'):
    if x not in privacy: fail(f'privacy missing {x}')
terms=' '.join((ROOT/'terms.html').read_text(encoding='utf-8').lower().split())
for x in ('no automatic offer','intellectual property','nothing in these terms excludes','law of england and wales'):
    if x not in terms: fail(f'terms missing {x}')
if 'Disallow: /' not in (ROOT/'robots.txt').read_text(encoding='utf-8'): fail('robots containment')

print('PASS: current proposition, Catalogue-only HOC-015 entry route, HOC-015, contact, legal, accessibility and noindex containment baseline')
