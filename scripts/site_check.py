from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HTML = {'index.html', '404.html'}
HTML_FILES = sorted(p for p in ROOT.glob('*.html') if p.is_file())
STYLE = ROOT / 'assets' / 'hoc-rebuild.css'
MARK = ROOT / 'assets' / 'hoc-mark.svg'
ROBOTS = ROOT / 'robots.txt'

REQUIRED_COPY = (
    'we build useful businesses.',
    'house of carol develops products, services and ventures designed to solve real problems and create genuine customer value.',
    'we start small, test ideas against reality and invest further only when they earn it.',
    'what we build',
    'house of carol can develop businesses in more than one field.',
    'they must be useful, commercially sound and worth doing properly.',
    'we do not keep ideas alive simply because we are fond of them.',
    'how we work',
    'useful before complicated.',
    'start with the problem, not the technology.',
    'evidence before expansion.',
    'real customers and real results matter more than internal enthusiasm.',
    'built properly.',
    'clear thinking, good design and professional standards are part of the work.',
    'long-term where it earns it.',
    'good businesses should become dependable, repeatable and capable of growing.',
    'our businesses and ventures',
    'bristol, united kingdom',
)

FORBIDDEN = (
    'grand house', 'fields', 'threshold', '52 departments', '330-function',
    'customer 000', 'engine architecture', 'workflow implementation',
    'website release assurance', 'coming soon', 'current ventures',
    'portfolio category', 'ai-powered', 'our ai team', 'contact us',
)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None; self.viewport = False; self.robots = None; self.csp = None
        self.title_count = 0; self.h1_count = 0; self.descriptions = []
        self.forms = []; self.scripts = []; self.inline_scripts = 0; self.hrefs = []
    def handle_starttag(self, tag, attrs_list):
        attrs = {k:(v or '') for k,v in attrs_list}
        if tag == 'html': self.lang = attrs.get('lang')
        elif tag == 'title': self.title_count += 1
        elif tag == 'h1': self.h1_count += 1
        elif tag == 'meta':
            if attrs.get('name') == 'viewport': self.viewport = bool(attrs.get('content'))
            elif attrs.get('name') == 'robots': self.robots = attrs.get('content')
            elif attrs.get('name') == 'description': self.descriptions.append(attrs.get('content'))
            elif attrs.get('http-equiv','').lower() == 'content-security-policy': self.csp = attrs.get('content')
        elif tag == 'form': self.forms.append(attrs)
        elif tag == 'script':
            if attrs.get('src'): self.scripts.append(attrs['src'])
            else: self.inline_scripts += 1
        elif tag == 'a' and attrs.get('href'): self.hrefs.append(attrs['href'])

def fail(msg): raise SystemExit(f'FAIL: {msg}')

def parse(path):
    p = Parser(); text = path.read_text(encoding='utf-8'); p.feed(text); return p, text

if {p.name for p in HTML_FILES} != EXPECTED_HTML:
    fail(f'root HTML must be exactly {sorted(EXPECTED_HTML)}; found {[p.name for p in HTML_FILES]}')
for item in (STYLE, MARK, ROBOTS):
    if not item.exists(): fail(f'missing {item.relative_to(ROOT)}')

for html in HTML_FILES:
    p, text = parse(html)
    if p.lang != 'en-GB': fail(f'{html.name}: lang must be en-GB')
    if p.title_count != 1 or p.h1_count != 1: fail(f'{html.name}: expected one title and one h1')
    if not p.viewport: fail(f'{html.name}: viewport missing')
    if p.robots != 'noindex,nofollow': fail(f'{html.name}: containment missing')
    if not p.csp: fail(f'{html.name}: CSP missing')
    for directive in ("object-src 'none'", "base-uri 'self'", "script-src 'none'", "form-action 'none'", "connect-src 'none'"):
        if directive not in p.csp: fail(f'{html.name}: CSP missing {directive}')
    if p.forms or p.scripts or p.inline_scripts: fail(f'{html.name}: interactive/data-collection code present')
    if len(p.descriptions) != 1 or not p.descriptions[0].strip(): fail(f'{html.name}: description missing')
    for href in p.hrefs:
        parsed = urlparse(href)
        if parsed.scheme or parsed.netloc:
            fail(f'{html.name}: external link present: {href}')
        target = (html.parent / (parsed.path or html.name)).resolve()
        if target.suffix == '': target = target / 'index.html'
        if not target.exists(): fail(f'{html.name}: broken local link {href}')

index_text = (ROOT / 'index.html').read_text(encoding='utf-8').lower()
for phrase in REQUIRED_COPY:
    if phrase not in index_text: fail(f'index missing approved copy: {phrase}')
for phrase in FORBIDDEN:
    if phrase in index_text: fail(f'index contains forbidden/stale material: {phrase}')
for forbidden_element in ('<nav', '<form', '<script', 'mailto:', 'tel:'):
    if forbidden_element in index_text: fail(f'index contains unauthorised element: {forbidden_element}')
if index_text.count('<section') != 4:
    fail('index must contain exactly four public content sections')

css = STYLE.read_text(encoding='utf-8').lower()
for token in ('--carol:#081d2d', '--claret:#7a1e2e', 'prefers-reduced-motion', ':focus-visible'):
    if token not in css: fail(f'CSS missing brand/accessibility token: {token}')
if 'Disallow: /' not in ROBOTS.read_text(encoding='utf-8'):
    fail('robots containment missing')

print('PASS: minimal parent-company site, exact content envelope, no enquiry/data collection, containment and accessibility/security baseline')
