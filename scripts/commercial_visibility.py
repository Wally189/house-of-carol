from pathlib import Path
import html,json,re
ROOT=Path(__file__).resolve().parents[1]
O=json.loads((ROOT/'data/commercial_visibility_20261021.json').read_text())['offers']
F=['operations','ai-digital','commercial','learning','research','charity-public','church-parish']
READY=[x for x in O if x['directory_eligible']];HOLD=[x for x in O if not x['directory_eligible']]
assert len(O)==54 and len(READY)==12 and len(HOLD)==42 and all(not x['transaction_authorised'] for x in O)
CARD=re.compile(r'<article class="service-entry" id="hoc-(\d{3})" data-offer-id="(HOC-\d{3})">[\s\S]*?</article>')
W={}
def fail(m):raise SystemExit('VISIBILITY BUILD FAIL: '+m)
for f in F:
 p=ROOT/f'catalogue-{f}.html';h=p.read_text();items=[x for x in O if x['family']==f]
 if [m.group(2) for m in CARD.finditer(h)]!=[x['offer_id'] for x in items]:fail('source order '+f)
 shown={x['offer_id'] for x in items if x['directory_eligible']}
 h=CARD.sub(lambda m:m.group(0).replace('View service →','Explore defined service →') if m.group(2) in shown else '',h)
 intro=re.search(r'<p class="service-family-intro">.*?</p>',h,re.S)
 if not intro:fail('intro '+f)
 msg=('The defined services below may be discussed by enquiry. A live engagement requires confirmed suitability, capacity, insurance, final price and written terms.' if shown else 'No service in this area is currently open for a new commissioned engagement. You can describe your organisational need through the general enquiry route; no work is accepted without an appropriate agreement.')
 h=h.replace(intro.group(),'<p class="service-family-intro">'+msg+'</p>',1)
 anchors=''.join('<span id="hoc-'+x['offer_id'][4:]+'" hidden aria-hidden="true"></span>' for x in items if not x['directory_eligible'])
 generic=('<article class="service-entry service-enquiry-entry"><a class="service-card-link" href="contact.html"><div class="service-card-heading"><h3>Discuss your organisational need</h3><p class="service-for">This family is not currently open for commissioned work.</p></div><div class="service-card-copy"><p>An enquiry does not commit either party to work.</p><span class="service-cue" aria-hidden="true">General enquiry →</span></div></a></article>') if not shown else ''
 h=h.replace('<div class="service-list">','<div class="service-list">'+anchors+generic,1)
 h=re.sub(r'<p class="eyebrow">\d+ services</p>','<p class="eyebrow">'+('Defined services for enquiry' if shown else 'General enquiry route')+'</p>',h,count=1)
 W[p]=h
p=ROOT/'catalogue.html';h=p.read_text()
h=h.replace('54 services · seven areas','Seven practical service areas').replace('Fifty-four practical House of Carol services across operations, AI and digital work, commercial processes, learning, research, charities, public-sector organisations, churches and parishes.','Seven practical areas of organisational work; defined services are listed for enquiry only where delivery controls permit.')
h=h.replace('Each service page explains what the work is for, what you receive and the boundaries of the service.','Enquire about a defined service; agreements depend on suitability, capacity, insurance, final price and written terms.')
for f in F:
 orig='<p class="eyebrow">'+str(sum(x['family']==f for x in O))+' services</p>'
 if orig not in h:fail('category count '+f)
 h=h.replace(orig,'<p class="eyebrow">'+('Defined service options' if any(x['family']==f and x['directory_eligible'] for x in O) else 'General enquiry only')+'</p>',1)
h,n=re.subn(r'\s*<section class="section admin-service-section" aria-labelledby="admin-service-heading">[\s\S]*?</section>','',h,count=1)
if n!=1:fail('HOC065 featured section')
W[p]=h
STYLE='assets/hoc-commercial-eligibility.css'
for x in O:
 p=ROOT/x['source_route'];h=p.read_text()
 if 'commercial-eligibility-notice' in h:fail('already altered '+x['source_route'])
 if not re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"',h,re.I):fail('noindex '+x['source_route'])
 if x['directory_eligible']:
  heading='Defined service for enquiry';message='This is a defined service for enquiry, not an immediate purchase. Engagements are subject to confirmed suitability, capacity, professional cover where needed, final fee, written terms and House of Carol acceptance.'
  if x['reason']=='Specific PI confirmation pending':message+=' The insurance decision must be settled before live work.'
 elif x['maturity']=='S3_S4_PI_HOLD':
  heading='Not available to commission';message='This service is not currently open for commissioned work. Suitable professional indemnity cover is outstanding. This page is a service description, not a current offer.'
 elif x['offer_id']=='HOC-065':
  heading='Not available to commission';message='This monthly service is not currently open to new engagements. The £950 per month figure is a pricing hypothesis, not a confirmed offer. This page may be viewed for information only.'
 else:
  heading='Not available to commission';message='This service is not currently open to new engagements. Its description and any price figures are indicative reference material, not an offer to undertake the work. Use the general enquiry route to describe your organisational need.'
 note='<aside class="commercial-eligibility-notice" role="note" aria-label="Service availability"><div class="shell"><p class="availability-label">'+html.escape(heading)+'</p><p>'+html.escape(message)+'</p></div></aside>'
 start=h.find('<nav aria-label="Breadcrumb"');end=h.find('</nav>',start)+len('</nav>') if start>=0 else 0
 if not end:fail('breadcrumb '+x['source_route'])
 h=h[:end]+note+h[end:]
 ns=h.find('class="next-service-module"');ne=h.find('</section>',ns) if ns>=0 else -1
 if ns>=0 and ne>ns:
  block=h[ns:ne]
  if re.search(r'href="(?:[^"]+\.html)"',block):
   block=block.replace('<div class="worked-example-findings">','<p class="related-availability">Some related service descriptions are not available to commission. Check the destination page for current availability.</p><div class="worked-example-findings">',1)
  for held in HOLD:block=block.replace('href="'+held['source_route']+'"','href="'+held['source_route']+'" data-related-service-unavailable="true"')
  h=h[:ns]+block+h[ne:]
 if '<link rel="stylesheet" href="'+STYLE+'">' not in h:h=h.replace('</head>','<link rel="stylesheet" href="'+STYLE+'"></head>',1)
 W[p]=h
for p,h in W.items():p.write_text(h)
print('VISIBILITY PASS: 7 families; 12 enquiry routes; 42 held unpromoted; all 54 source pages preserved')
