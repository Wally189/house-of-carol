from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]; HTML=[ROOT/n for n in ('index.html','privacy.html','terms.html','404.html')]
class Parser(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True); self.lang=None; self.viewport=False; self.robots=None; self.csp=None; self.titles=0; self.h1s=0; self.descriptions=[]; self.forms=[]; self.scripts=[]; self.labels=set(); self.controls=set(); self.hrefs=[]
 def handle_starttag(self,tag,attrs_list):
  a={k:(v or '') for k,v in attrs_list}
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
  elif tag=='a' and a.get('href'): self.hrefs.append(a['href'])
def fail(m): raise SystemExit(f'FAIL: {m}')
for item in (*HTML,ROOT/'assets/hoc-rebuild.css',ROOT/'assets/hoc-contact.css',ROOT/'assets/hoc-mark.svg',ROOT/'robots.txt'):
 if not item.exists(): fail(f'missing {item.relative_to(ROOT)}')
for page in HTML:
 p=Parser(); p.feed(page.read_text(encoding='utf-8'))
 if p.lang!='en-GB' or not p.viewport or p.titles!=1 or p.h1s!=1 or len(p.descriptions)!=1: fail(f'{page.name}: metadata')
 if p.robots!='noindex,nofollow': fail(f'{page.name}: containment')
 if not p.csp or any(x not in p.csp for x in ("object-src 'none'","base-uri 'self'","script-src 'none'","connect-src 'none'")): fail(f'{page.name}: CSP')
 if p.scripts: fail(f'{page.name}: scripts')
 if p.controls-p.labels: fail(f'{page.name}: unlabelled controls')
 for href in p.hrefs:
  u=urlparse(href)
  if u.scheme in ('mailto','tel','https'): continue
  if not (ROOT/(u.path or page.name)).resolve().exists(): fail(f'{page.name}: broken link {href}')
home=HTML[0].read_text(encoding='utf-8').lower(); p=Parser(); p.feed(home)
if len(p.forms)!=1 or p.forms[0].get('action')!='https://formspree.io/f/mgvgrgvb' or p.forms[0].get('method','').lower()!='post': fail('home: approved contact route')
for x in ('we build useful businesses.','what we build','how we work','our businesses and ventures','alan w gallagher trading as house of carol','116 knole lane','alanwgallagher1@gmail.com','07933 657446'):
 if x not in home: fail(f'home missing {x}')
if 'enquiries@houseofcarol.com' in home: fail('home: unverified domain email remains')
for x in ('ai-powered','industry-leading','world-class','52 departments','customer 000'):
 if x in home: fail(f'unsupported/internal claim {x}')
privacy=' '.join(HTML[1].read_text(encoding='utf-8').lower().split())
for x in ('data controller','legitimate interests','formspree','united states','standard contractual clauses','information commissioner','cookies and analytics','alanwgallagher1@gmail.com'):
 if x not in privacy: fail(f'privacy missing {x}')
if 'enquiries@houseofcarol.com' in privacy: fail('privacy: unverified domain email remains')
terms=' '.join(HTML[2].read_text(encoding='utf-8').lower().split())
for x in ('no automatic offer','intellectual property','nothing in these terms excludes','law of england and wales','alanwgallagher1@gmail.com'):
 if x not in terms: fail(f'terms missing {x}')
if 'enquiries@houseofcarol.com' in terms: fail('terms: unverified domain email remains')
if 'Disallow: /' not in (ROOT/'robots.txt').read_text(encoding='utf-8'): fail('robots containment')
print('PASS: preserved content/brand, verified contact identity, privacy, terms, accessibility and containment baseline')
