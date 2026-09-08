from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    'index.html',
    'catalogue.html',
    'process-design-sprint.html',
    'about.html',
    'privacy.html',
    'terms.html',
    '404.html',
)
HTML = [ROOT / n for n in NAMES]

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
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'title':
            self.titles += 1
        elif tag == 'h1':
            self.h1s += 1
        elif tag == 'meta':
            if a.get('name') == 'viewport':
                self.viewport = bool(a.get('content'))
            elif a.get('name') == 'robots':
                self.robots = a.get('content')
            elif a.get('name') == 'description':
                self.descriptions.append(a.get('content'))
            elif a.get('http-equiv', '').lower() == 'content-security-policy':
                self.csp = a.get('content')
        elif tag == 'form':
            self.forms.append(a)
        elif tag == 'script':
            self.scripts.append(a)
        elif tag == 'label' and a.get('for'):
            self.labels.add(a['for'])
        elif tag in ('input', 'textarea', 'select') and a.get('id') and a.get('type') != 'hidden':
            self.controls.add(a['id'])
        elif tag == 'a' and a.get('href'):
            self.hrefs.append(a['href'])

def fail(message):
    raise SystemExit(f'FAIL: {message}')

required_files = [
    *HTML,
    ROOT / 'assets/hoc-rebuild.css',
    ROOT / 'assets/hoc-contact.css',
    ROOT / 'assets/hoc-catalogue.css',
    ROOT / 'assets/hoc-mark.svg',
    ROOT / 'robots.txt',
]
for item in required_files:
    if not item.exists():
        fail(f'missing {item.relative_to(ROOT)}')

for page in HTML:
    parser = Parser()
    parser.feed(page.read_text(encoding='utf-8'))
    if parser.lang != 'en-GB' or not parser.viewport or parser.titles != 1 or parser.h1s != 1 or len(parser.descriptions) != 1:
        fail(f'{page.name}: metadata')
    if parser.robots != 'noindex,nofollow':
        fail(f'{page.name}: containment')
    if not parser.csp or any(token not in parser.csp for token in ("object-src 'none'", "base-uri 'self'", "script-src 'none'")):
        fail(f'{page.name}: CSP')
    if parser.scripts:
        fail(f'{page.name}: scripts')
    if parser.controls - parser.labels:
        fail(f'{page.name}: unlabelled controls')
    for href in parser.hrefs:
        parsed = urlparse(href)
        if parsed.scheme in ('mailto', 'tel', 'https'):
            continue
        target = ROOT / (parsed.path or page.name)
        if not target.resolve().exists():
            fail(f'{page.name}: broken link {href}')

home = (ROOT / 'index.html').read_text(encoding='utf-8').lower()
home_parser = Parser()
home_parser.feed(home)
if len(home_parser.forms) != 1 or home_parser.forms[0].get('action') != 'https://formspree.io/f/mgvgrgvb' or home_parser.forms[0].get('method', '').lower() != 'post':
    fail('home: approved contact route')
for phrase in (
    'a useful place for difficult business work.',
    'start with the job, not the jargon.',
    'one-process improvement sprint',
    'catalogue.html',
    'process-design-sprint.html',
):
    if phrase not in home:
        fail(f'home missing {phrase}')

catalogue = (ROOT / 'catalogue.html').read_text(encoding='utf-8').lower()
for phrase in (
    'useful work, with a clear boundary.',
    'one important business process, properly sorted out.',
    '£1,500',
    'not yet released as a fixed offer',
    'process-design-sprint.html',
):
    if phrase not in catalogue:
        fail(f'catalogue missing {phrase}')

product = (ROOT / 'process-design-sprint.html').read_text(encoding='utf-8').lower()
for phrase in (
    "your business shouldn't depend on one person remembering how everything works.",
    '£1,500',
    'before and after should be obvious.',
    'what we need from you',
    'worth buying only when the problem is real.',
    'a real person accountable for the result.',
    'alan w gallagher',
):
    if phrase not in product:
        fail(f'HOC-015 page missing {phrase}')

for text, label in ((home, 'home'), (catalogue, 'catalogue'), (product, 'HOC-015')):
    for forbidden in ('ai-powered', 'industry-leading', 'world-class', '52 departments', 'customer 000', 'trusted by', 'guaranteed savings', 'tender-review.html'):
        if forbidden in text:
            fail(f'{label}: unsupported/internal/stale item {forbidden}')

privacy = ' '.join((ROOT / 'privacy.html').read_text(encoding='utf-8').lower().split())
for phrase in ('data controller', 'legitimate interests', 'formspree', 'united states', 'standard contractual clauses', 'information commissioner', 'cookies and analytics', 'alanwgallagher1@gmail.com'):
    if phrase not in privacy:
        fail(f'privacy missing {phrase}')

terms = ' '.join((ROOT / 'terms.html').read_text(encoding='utf-8').lower().split())
for phrase in ('no automatic offer', 'intellectual property', 'nothing in these terms excludes', 'law of england and wales', 'alanwgallagher1@gmail.com'):
    if phrase not in terms:
        fail(f'terms missing {phrase}')

if 'Disallow: /' not in (ROOT / 'robots.txt').read_text(encoding='utf-8'):
    fail('robots containment')

print('PASS: current House, catalogue, HOC-015, contact, legal, accessibility and noindex containment baseline')
