import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
from seo_policy import INDEXABLE, canonical

ROOT = Path(__file__).resolve().parents[1]
CORE_PAGES = ['index.html','how-it-works.html','catalogue.html','about.html','contact.html','privacy.html','terms.html','404.html']
AREA_PAGES = ["catalogue-operations.html","catalogue-ai-digital.html","catalogue-commercial.html","catalogue-learning.html","catalogue-research.html","catalogue-charity-public.html","catalogue-church-parish.html"]
EXPECTED_NAV = ['index.html','how-it-works.html','catalogue.html','about.html','contact.html']
REQUIRED_ASSETS = ['assets/hoc-commercial-eligibility.css','assets/hoc-rebuild.css','assets/hoc-contact.css','assets/hoc-catalogue.css','assets/hoc-service.css','assets/hoc-mark.svg','robots.txt']
FORM_ENDPOINT = 'https://formspree.io/f/mgvgrgvb'

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
area_links=re.findall(r'<article class="area-entry">\s*<a class="area-card-link" href="([^"]+\.html)">', catalogue_text)
if area_links!=AREA_PAGES: fail('main catalogue area links/order')

v=json.loads((ROOT/'data/commercial_visibility_20261021.json').read_text())['offers']
if len(v)!=54 or len({x['offer_id'] for x in v})!=54 or sum(x['directory_eligible'] for x in v)!=12:fail('54/12 portfolio contract')
entries=[];area_products={}
for area in AREA_PAGES:
 t=(ROOT/area).read_text()
 if re.search(r'£\s?\d',t):fail(area+': prices must remain on product pages')
 found=re.findall(r'<article class="service-entry(?: [^"]*)?"(?: id="hoc-\d{3}")? data-offer-id="(HOC-\d{3})">\s*<a class="service-card-link" href="([^"]+\.html)">',t,re.S)
 items=[x for x in v if 'catalogue-'+x['family']+'.html'==area]
 expected=[(x['offer_id'],x['source_route']) for x in items if x['directory_eligible']]
 if found!=expected:fail(area+': verified only ready enquiry choices')
 area_products[area]=items;entries.extend(found)
if len(entries)!=12 or len(set(x[0] for x in entries))!=12:fail('12 eligible links')
products=[x['source_route'] for x in v]
if len(set(products))!=54:fail('all 54 source pages')

PUBLIC_PAGES=CORE_PAGES+AREA_PAGES+products
for name in PUBLIC_PAGES+REQUIRED_ASSETS:
    if not (ROOT/name).exists(): fail('missing '+name)

parsers={name:parsed(name) for name in PUBLIC_PAGES}
for name,p in parsers.items():
    text=(ROOT/name).read_text(encoding='utf-8')
    if p.lang!='en-GB' or not p.viewport or p.titles!=1 or p.h1s!=1 or len(p.descriptions)!=1: fail(name+': baseline metadata')
    if p.robots!=('index,follow' if name in INDEXABLE else 'noindex,nofollow'): fail(name+': route-specific indexing policy')
    if name in INDEXABLE and f'<link rel="canonical" href="{canonical(name)}">' not in text: fail(name+': canonical missing')
    if not p.csp or any(d not in p.csp for d in ("object-src 'none'","base-uri 'self'","script-src 'none'","style-src 'self'")): fail(name+': CSP')
    if p.scripts: fail(name+': scripts present')
    if re.search(r'\sstyle\s*=', text, re.I): fail(name+': inline style is incompatible with CSP style-src self')
    if p.main_nav_hrefs!=EXPECTED_NAV: fail(name+': main navigation')
    if p.controls-p.labels: fail(name+': unlabelled controls')

robots=(ROOT/'robots.txt').read_text(encoding='utf-8')
if not re.search(r'(?im)^User-agent:\s*\*\s*$', robots): fail('robots missing universal user agent')
if re.search(r'(?im)^Disallow:\s*/\s*$', robots): fail('robots blocks crawlers from reading page noindex directives')

for name,p in parsers.items():
    for href in p.hrefs:
        u=urlparse(href)
        if u.scheme in ('mailto','tel','https') or href.startswith('#'): continue
        target=ROOT/(u.path or name)
        if not target.exists(): fail(f'{name}: broken link {href}')

for area,items in area_products.items():
 ap=parsers[area]
 for x in items:
  product=x['source_route'];expected=1 if x['directory_eligible'] else 0
  if ap.hrefs.count(product)!=expected:fail(area+': wrong promotion '+product)
  pp=parsers[product]
  if not any(href==area or href.startswith(area+'#') for href in pp.hrefs):fail(product+': family backlink')
  if 'catalogue.html' not in pp.hrefs or 'index.html' not in pp.hrefs:fail(product+': hierarchy')
  if ('Defined service for enquiry' if x['directory_eligible'] else 'Not available to commission') not in (ROOT/product).read_text():fail(product+': availability disclosure')

contact=parsers['contact.html']
contact_text=(ROOT/'contact.html').read_text(encoding='utf-8')
all_forms=[(n,f) for n,p in parsers.items() for f in p.forms]
if len(all_forms)!=2 or any(n!='contact.html' for n,_ in all_forms): fail('contact form location/count')
if len(contact.forms)!=2: fail('contact form count')
for form in contact.forms:
    if form.get('action')!=FORM_ENDPOINT: fail('contact form Formspree endpoint')
    if form.get('method','').lower()!='post': fail('contact form method')
if 'form-action https://formspree.io' not in (contact.csp or ''): fail('contact CSP must allow only the authorised Formspree form origin')
if contact_text.count(FORM_ENDPOINT)!=2: fail('contact page must contain the authorised Formspree endpoint twice')
if '<fieldset disabled' in contact_text or re.search(r'<button[^>]*type="submit"[^>]*disabled', contact_text): fail('contact forms remain technically held')
expected_controls={'name','email','message','call-name','call-telephone','call-email'}
if contact.controls!=expected_controls or contact.controls-contact.labels: fail('contact controls')
for required_control in expected_controls:
    if not re.search(r'<(?:input|textarea)[^>]*id="'+required_control+r'"[^>]*\brequired\b', contact_text): fail('contact required control '+required_control)
if len(re.findall(r'<input[^>]*type="radio"[^>]*name="preferred_call_time"', contact_text))!=4: fail('call-request time option count')
for value in ('8:00am','12 noon','4:30pm',"I'm flexible"):
    if f'value="{value}"' not in contact_text: fail('call-request time option '+value)
if not re.search(r'<input[^>]*type="radio"[^>]*name="preferred_call_time"[^>]*value="8:00am"[^>]*\brequired\b', contact_text): fail('call-request time group required state')
if 'name="_subject" value="Website enquiry — House of Carol"' not in contact_text: fail('enquiry subject discriminator')
if 'name="_subject" value="Introductory call request — House of Carol"' not in contact_text: fail('call-request subject discriminator')
if 'name="request_type" value="Introductory call request"' not in contact_text: fail('call-request type discriminator')

for product in products:
    text=(ROOT/product).read_text(encoding='utf-8').lower()
    if 'pricing' not in text and not re.search(r'£\s?\d', text): fail(product+': pricing information missing')

all_text='\n'.join((ROOT/n).read_text(encoding='utf-8').lower() for n in PUBLIC_PAGES)
for claim in ('industry-leading','world-class','52 departments','customer 000'):
    if claim in all_text: fail('unsupported/internal claim '+claim)
if 'alanwgallagher1@gmail.com' in all_text: fail('underlying personal Gmail exposed in customer-facing estate')
if all_text.count(FORM_ENDPOINT)!=2: fail('Formspree endpoint must appear exactly twice in customer-facing estate')

privacy=' '.join((ROOT/'privacy.html').read_text(encoding='utf-8').lower().split())
for t in ('data controller','alan@houseofcarol.co.uk','legitimate interests','right to object','information commissioner','cookies and analytics','formspree, inc.','website-form processor','united states','standard contractual clauses','telephone number','preferred call time'):
    if t not in privacy: fail('privacy missing '+t)
terms=' '.join((ROOT/'terms.html').read_text(encoding='utf-8').lower().split())
for t in ('alan@houseofcarol.co.uk','no automatic offer','intellectual property','nothing in these terms excludes','law of england and wales'):
    if t not in terms: fail('terms missing '+t)

# NAVIGATION CONTRACT: homepage areas and exact service returns
_home=(ROOT/'index.html').read_text(encoding='utf-8')
for _dest in AREA_PAGES:
    if f'href="{_dest}"' not in _home:
        fail('homepage area route missing '+_dest)

for _area,items in area_products.items():
 for x in items:
  ident='hoc-'+x['offer_id'][4:];product=x['source_route']
  if ident not in parsers[_area].ids:fail(_area+': missing original anchored ID '+ident)
  if (ROOT/product).read_text().count('href="'+_area+'#'+ident+'"')<2:fail(product+': family return link')

# INTERACTION CONTRACT: catalogue cards and service rows
_catalogue=(ROOT/'catalogue.html').read_text(encoding='utf-8')
if _catalogue.count('class="area-card-link"') != 7:
    fail('catalogue whole-card link count')
if _catalogue.count('class="area-cue"') != 7:
    fail('catalogue area cue count')
if 'class="text-link"' in _catalogue and 'View ' in _catalogue:
    fail('duplicate area navigation link remains')

for _area in AREA_PAGES:
    _txt=(ROOT/_area).read_text(encoding='utf-8')
    _service_count=len(re.findall(r'<article class="service-entry(?: [^"]*)?"', _txt))
    if _txt.count('class="service-card-link"') != _service_count:
        fail(_area+': whole-row link count mismatch')
    if _txt.count('class="service-cue"') != _service_count:
        fail(_area+': service cue count mismatch')

print('PASS: 7-area catalogue -> 7 area catalogues -> 12 enquiry entries and 42 held pages, all 54 product pages verified; hierarchy, pricing separation, metadata, CSP-compatible styling, noindex crawlability, navigation, links, authorised Formspree enquiry and call-request routes, branded identity and legal checks pass')
