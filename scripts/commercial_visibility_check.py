from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/commercial_visibility_20261021.json').read_text());O=D['offers']
F=['operations','ai-digital','commercial','learning','research','charity-public','church-parish']
def fail(m):raise SystemExit('ELIGIBILITY FAIL: '+m)
if len(O)!=54 or len({x['offer_id'] for x in O})!=54 or len({x['source_route'] for x in O})!=54:fail('54 identities')
if D['portfolio_total']!=65 or D['held_unlisted_offers']!=11:fail('65 portfolio')
if sum(x['directory_eligible'] for x in O)!=12 or any(x['transaction_authorised'] for x in O):fail('no automatic sale')
for k,n in [('S4_TRANSACTION_CANDIDATE',12),('S2_INTERNAL',30),('S1',8),('S3_S4_PI_HOLD',3),('S3_WEB_CANDIDATE_S2_EXTERNAL_HOLD',1)]:
 if sum(x['maturity']==k for x in O)!=n:fail('status counts '+k)
if any((x['maturity']=='S4_TRANSACTION_CANDIDATE')!=x['directory_eligible'] for x in O):fail('no lifecycle uplift')
for fam in F:
 h=(ROOT/f'catalogue-{fam}.html').read_text()
 ids=re.findall(r'<article class="service-entry" id="hoc-\d{3}" data-offer-id="(HOC-\d{3})">',h)
 expected=[x['offer_id'] for x in O if x['family']==fam and x['directory_eligible']]
 if ids!=expected:fail(fam+' exact catalogue eligibility')
 if bool('service-enquiry-entry' in h)==bool(expected):fail(fam+' contact-only family mismatch')
 for x in O:
  if x['family']==fam and not x['directory_eligible'] and f'id="hoc-{x["offer_id"][4:]}" hidden' not in h:fail('lost original deep-link anchor')
for x in O:
 h=(ROOT/x['source_route']).read_text()
 if h.count('class="commercial-eligibility-notice"')!=1:fail('availability notice '+x['offer_id'])
 if not re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"',h,re.I):fail('held noindex '+x['offer_id'])
 if 'assets/hoc-commercial-eligibility.css' not in h:fail('notice stylesheet '+x['offer_id'])
 label='Defined service for enquiry' if x['directory_eligible'] else 'Not available to commission'
 if label not in h:fail('truthfulness '+x['offer_id'])
 if x['maturity']=='S3_S4_PI_HOLD' and 'indemnity cover is outstanding' not in h:fail('PI hold '+x['offer_id'])
 if x['offer_id']=='HOC-065' and ('£950 per month' not in h or 'pricing hypothesis' not in h):fail('HOC065 price hypothesis')
 if x['directory_eligible'] and ('not an immediate purchase' not in h or 'written terms' not in h):fail('terms gate '+x['offer_id'])
cat=(ROOT/'catalogue.html').read_text()
if 'admin-service-section' in cat or cat.count('class="area-card-link"')!=7:fail('all seven family paths, no S2 feature')
print('PASS: 7 families, 12 S4 enquiry candidates, 42 held, 54 noindex direct pages, PI and transaction gates, no portfolio deletion')
