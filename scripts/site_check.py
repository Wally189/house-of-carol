from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re

ROOT = Path(__file__).resolve().parents[1]
CORE_PAGES = ['index.html','how-it-works.html','catalogue.html','about.html','contact.html','privacy.html','terms.html','404.html']
EXPECTED_NAV = ['index.html','how-it-works.html','catalogue.html','about.html','contact.html']
REQUIRED_ASSETS = ['assets/hoc-rebuild.css','assets/hoc-contact.css','assets/hoc-catalogue.css','assets/hoc-service.css','assets/hoc-mark.svg','robots.txt']

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang=None; self.viewport=False; self.robots=None; self.csp=None
        self.titles=0; self.h1s=0; self.descriptions=[]; self.forms=[]; self.scripts=[]
        self.labels=set(); self.controls=set(); self.hrefs=[]; self.ids=set(); self.main_nav_hrefs=[]; self._nav=None
    def handle_starttag(self, tag, attrs_list):
        a={k:(v or '') for k,v in attrs_list}
        if a.get('id'): self.ids.add(a['id'])
        if tag=='html': self.lang=a.get('lang')
        elif tag=='title': self.titles+=1
        elif tag=='h1': self.h1s+=1
        elif tag=='meta':
            if a.get('name')=='viewport': self.viewport=bool(a.get('content'))
            elif a.get('name')=='robots': self.robots=a.get('content')
            elif a.get('name')=='description': self.descriptions.append(a.get('content'))
            elif a.get('http-equiv','').lower()=='content-security-policy': self.csp=a.get('content')
        elif tag=='form': self.forms.append(a)
        elif tag=='script': self.scripts.append(a)
        elif tag=='label' and a.get('for'): self.labels.add(a['for'])
        elif tag in ('input','textarea','select') and a.get('id') and a.get('type')!='hidden': self.controls.add(a['id'])
        elif tag=='nav': self._nav='main' if 'main-nav' in a.get('class','').split() else 'other'
        elif tag=='a' and a.get('href'):
            self.hrefs.append(a['href'])
            if self._nav=='main': self.main_nav_hrefs.append(a['href'])
    def handle_endtag(self, tag):
        if tag=='nav': self._nav=None

def fail(m): raise SystemExit('FAIL: '+m)
def parsed(name):
    p=Parser(); p.feed((ROOT/name).read_text(encoding='utf-8')); return p

catalogue_text=(ROOT/'catalogue.html').read_text(encoding='utf-8')
if re.search(r'£\s?\d', catalogue_text): fail('catalogue contains a displayed price')
entries=re.findall(r'<article class="service-entry" data-offer-id="(HOC-\d{3})">\s*<h3><a href="([^"]+\.html)">', catalogue_text, flags=re.S)
if len(entries)!=52: fail(f'catalogue service-link count {len(entries)}')
ids=[x[0] for x in entries]; products=[x[1] for x in entries]
if len(set(ids))!=52 or len(set(products))!=52: fail('catalogue service IDs/routes are not unique')

PUBLIC_PAGES=CORE_PAGES+products
for name in PUBLIC_PAGES+REQUIRED_ASSETS:
    if not (ROOT/name).exists(): fail('missing '+name)

parsers={name:parsed(name) for name in PUBLIC_PAGES}
for name,p in parsers.items():
    if p.lang!='en-GB' or not p.viewport or p.titles!=1 or p.h1s!=1 or len(p.descriptions)!=1: fail(name+': baseline metadata')
    if p.robots!='noindex,nofollow': fail(name+': indexing containment')
    if not p.csp or any(d not in p.csp for d in ("object-src 'none'","base-uri 'self'","script-src 'none'")): fail(name+': CSP')
    if p.scripts: fail(name+': scripts present')
    if p.main_nav_hrefs!=EXPECTED_NAV: fail(name+': main navigation')
    if p.controls-p.labels: fail(name+': unlabelled controls')

if 'Disallow: /' not in (ROOT/'robots.txt').read_text(encoding='utf-8'): fail('robots containment')

for name,p in parsers.items():
    for href in p.hrefs:
        u=urlparse(href)
        if u.scheme in ('mailto','tel','https') or href.startswith('#'): continue
        target=ROOT/(u.path or name)
        if not target.exists(): fail(f'{name}: broken link {href}')

cat=parsers['catalogue.html']
for product in products:
    if cat.hrefs.count(product)!=1: fail('catalogue expected one link to '+product)

contact=parsers['contact.html']
all_forms=[(n,f) for n,p in parsers.items() for f in p.forms]
if len(all_forms)!=1 or all_forms[0][0]!='contact.html': fail('contact form location/count')
form=contact.forms[0]
if form.get('action')!='https://formspree.io/f/mgvgrgvb' or form.get('method','').lower()!='post': fail('contact route')
if contact.controls!={'name','email','message'} or contact.controls-contact.labels: fail('contact controls')

for product in products:
    text=(ROOT/product).read_text(encoding='utf-8').lower()
    if 'pricing' not in text and not re.search(r'£\s?\d', text): fail(product+': pricing information missing')

all_text='\n'.join((ROOT/n).read_text(encoding='utf-8').lower() for n in PUBLIC_PAGES)
for claim in ('industry-leading','world-class','52 departments','customer 000'):
    if claim in all_text: fail('unsupported/internal claim '+claim)

privacy=' '.join((ROOT/'privacy.html').read_text(encoding='utf-8').lower().split())
for t in ('data controller','legitimate interests','formspree','united states','standard contractual clauses','information commissioner','cookies and analytics'):
    if t not in privacy: fail('privacy missing '+t)
terms=' '.join((ROOT/'terms.html').read_text(encoding='utf-8').lower().split())
for t in ('no automatic offer','intellectual property','nothing in these terms excludes','law of england and wales'):
    if t not in terms: fail('terms missing '+t)

print('PASS: 52 catalogue services link to 52 detail pages; catalogue has no displayed prices; product pricing, metadata, containment, navigation, links, contact and legal checks pass')
