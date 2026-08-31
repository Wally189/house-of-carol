from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(p for p in ROOT.glob('*.html') if p.is_file())
EXPECTED_STYLE = 'assets/hoc-rebuild.css'
STYLE = ROOT / 'assets' / 'hoc-rebuild.css'
MARK = ROOT / 'assets' / 'hoc-mark.svg'
ROBOTS = ROOT / 'robots.txt'

BANNED_PUBLIC_PHRASES = (
    '52-hive','52 hive','engine architecture','maturity score','acquisition gate',
    'world-class','game-changing','industry-leading','cutting-edge','transformational',
    'cross-functional synergies','future-ready architecture','grand house','ai-powered',
    'waylight atlantic','alanwpgallagher.info','customer 000','330-function','our ai team'
)
BANNED_AI_SLUDGE = (
    'delve into','vibrant tapestry','seamless journey','unlock the power',
    'ever-evolving landscape','supercharge your business','unlock your potential'
)

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.hrefs=[]; self.scripts=[]; self.styles=[]; self.forms=[]
        self.lang=None; self.viewport=False; self.robots=None; self.csp=None
        self.title_count=0; self.h1_count=0; self.descriptions=[]; self.inline_scripts=0
    def handle_starttag(self, tag, attrs_list):
        attrs={k:(v or '') for k,v in attrs_list}
        if tag=='html': self.lang=attrs.get('lang')
        elif tag=='title': self.title_count+=1
        elif tag=='h1': self.h1_count+=1
        elif tag=='meta':
            if attrs.get('name')=='viewport': self.viewport=bool(attrs.get('content'))
            elif attrs.get('name')=='robots': self.robots=attrs.get('content')
            elif attrs.get('name')=='description': self.descriptions.append(attrs.get('content'))
            elif attrs.get('http-equiv','').lower()=='content-security-policy': self.csp=attrs.get('content')
        if 'id' in attrs:
            if attrs['id'] in self.ids: raise AssertionError(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs['id'])
        if tag=='a' and attrs.get('href'): self.hrefs.append(attrs['href'])
        elif tag=='script':
            if attrs.get('src'): self.scripts.append(attrs['src'])
            else: self.inline_scripts += 1
        elif tag=='link' and attrs.get('rel')=='stylesheet' and attrs.get('href'): self.styles.append(attrs['href'])
        elif tag=='form': self.forms.append(attrs)

def fail(message): raise SystemExit(f'FAIL: {message}')

def parse(path):
    parser=PageParser(); text=path.read_text(encoding='utf-8')
    try: parser.feed(text)
    except AssertionError as exc: fail(f'{path.name}: {exc}')
    lowered=text.lower()
    for phrase in (*BANNED_PUBLIC_PHRASES,*BANNED_AI_SLUDGE):
        if phrase in lowered: fail(f'{path.name}: banned inward/hype/sludge phrase present: {phrase}')
    return parser, text

if not HTML_FILES: fail('no root HTML pages found')
for item in (STYLE, MARK, ROBOTS):
    if not item.exists(): fail(f'missing {item.relative_to(ROOT)}')

pages={}; texts={}
for html in HTML_FILES:
    p,text=parse(html); pages[html.resolve()]=p; texts[html.resolve()]=text
    if p.lang!='en-GB': fail(f'{html.name}: lang must be en-GB')
    if p.title_count!=1 or p.h1_count!=1: fail(f'{html.name}: expected exactly one title and one h1')
    if not p.viewport: fail(f'{html.name}: viewport missing')
    if p.robots!='noindex,nofollow': fail(f'{html.name}: controlled-preview containment missing')
    if not p.csp: fail(f'{html.name}: CSP missing')
    for directive in ("object-src 'none'", "base-uri 'self'", "script-src 'none'", "form-action 'none'"):
        if directive not in p.csp: fail(f'{html.name}: CSP missing {directive}')
    if p.styles != [EXPECTED_STYLE]: fail(f'{html.name}: expected only {EXPECTED_STYLE}; found {p.styles}')
    if p.scripts or p.inline_scripts: fail(f'{html.name}: scripts present in static controlled preview')
    if len(p.descriptions)!=1 or not p.descriptions[0].strip(): fail(f'{html.name}: descriptive meta missing')
    if p.forms: fail(f'{html.name}: public form present before authorised contact activation')

def local_target(base, href):
    parsed=urlparse(href)
    if parsed.scheme in {'mailto','tel'}: return None
    if parsed.scheme or parsed.netloc:
        if parsed.scheme!='https': fail(f'{base.name}: non-https external link {href}')
        return None
    return (base.parent/(parsed.path or base.name)).resolve(), parsed.fragment or None

for base,p in pages.items():
    for href in p.hrefs:
        info=local_target(base,href)
        if info is None: continue
        target,frag=info
        if target.suffix=='': target=target/'index.html'
        if not target.exists(): fail(f'{base.name}: broken local link {href}')
        if frag and target.suffix=='.html':
            tp=pages.get(target.resolve())
            if tp is None: tp,_=parse(target)
            if frag not in tp.ids: fail(f'{base.name}: broken anchor {href}')

index=(ROOT/'index.html').resolve()
if index not in texts: fail('index.html missing')
index_text=texts[index].lower()
for required in ('house of carol','intelligence','judgement','impact','workflow implementation','website release assurance','controlled preview'):
    if required not in index_text: fail(f'index missing current brand/commercial truth: {required}')
for forbidden in ('customer 000','330-function','52 departments','our ai team'):
    if forbidden in index_text: fail(f'index leaks internal machinery: {forbidden}')
if 'class="card' in index_text or ' class="card' in index_text: fail('generic card component introduced')

css=STYLE.read_text(encoding='utf-8').lower()
for token in ('--carol:#081d2d','--claret:#7a1e2e','prefers-reduced-motion',':focus'):
    if token not in css: fail(f'CSS missing current brand/accessibility token: {token}')
robots=ROBOTS.read_text(encoding='utf-8')
if 'Disallow: /' not in robots: fail('robots containment missing')

print(f'PASS: {len(HTML_FILES)} pages — current House brand truth, controlled-preview containment, static integrity, no-form control, local links and anti-sludge checks')
