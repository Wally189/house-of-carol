from pathlib import Path
import re, sys
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT/'scripts/build_case_studies.py').read_text(encoding='utf-8')
block = re.search(r"PRODUCTS = \[(.*?)\]\n", text, re.S).group(1)
PRODUCTS = re.findall(r"'([^']+\.html)'", block)
EXAMPLES = ['worked-example-ai-workflow.html','worked-example-process-handover.html','worked-example-trade-account-customer-journey.html','worked-examples.html']
FORBIDDEN = ['customer 000','external proof required','owner gate','internal candidate','internal qa','proprietor-approved','lifecycle status','first-test','scope fit','service unit','governance kernel','source universe','temporal service',' bounded ','house ai-governance kernel','house ai-governance framework','bounded administrative process']
MALFORMED = ['requested what you need this service','current service only']
CANONICAL_NAMES = {
    'independent-document-review.html': 'AI Output Assurance & Red-Team Review',
    'shared-drive-cleanup.html': 'Document Control & Knowledge-System Cleanup',
    'management-information-and-kpi-setup.html': 'Management Information & KPI Setup',
}
CHURCH_ROUTES = {
    'church-and-parish-grant-funding-research.html',
    'church-grant-application-development-support.html',
    'church-building-funding-and-maintenance-roadmap.html',
    'parish-operations-and-administration-improvement.html',
    'parish-digital-and-ai-governance-starter-service.html',
    'parish-communications-service.html',
}
errors = []

def visible(html):
    html = re.sub(r'<(?:style|script)\b.*?</(?:style|script)>',' ',html,flags=re.I|re.S)
    html = re.sub(r'<[^>]+>',' ',html)
    html = unescape(html)
    return ' ' + re.sub(r'\s+',' ',html).casefold() + ' '

def description_metadata(html):
    values = []
    for tag in re.findall(r'<meta\b[^>]*>', html, re.I|re.S):
        if not re.search(r'\bname=["\']description["\']', tag, re.I):
            continue
        m = re.search(r'\bcontent=["\'](.*?)["\']', tag, re.I|re.S)
        if m:
            values.append(m.group(1))
    return ' ' + re.sub(r'\s+',' ',' '.join(values)).casefold() + ' '

for route in PRODUCTS:
    h = (ROOT/route).read_text(encoding='utf-8'); v = visible(h); meta = description_metadata(h)
    for term in FORBIDDEN:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
        if term in meta: errors.append(f'{route}: metadata internal term {term.strip()}')
    for phrase in MALFORMED:
        if phrase in v: errors.append(f'{route}: malformed customer-facing phrase {phrase}')
        if phrase in meta: errors.append(f'{route}: malformed metadata phrase {phrase}')
    if route in CHURCH_ROUTES and ' temporal ' in v:
        errors.append(f'{route}: customer-visible temporal language remains')
    expected_name = CANONICAL_NAMES.get(route)
    if expected_name and expected_name.casefold() not in v:
        errors.append(f'{route}: canonical public name missing: {expected_name}')
    checks = {
      'single H1': len(re.findall(r'<h1\b',h,re.I)) == 1,
      'service visual': len(re.findall(r'<figure\b[^>]*class="[^"]*\bproduct-visual\b[^"]*\bcustomer-service-visual\b[^"]*"[^>]*>.*?<img\b[^>]*alt="[^"]+"',h,re.I|re.S)) == 1,
      'worked example': len(re.findall(r'<section\b[^>]*class="[^"]*\bworked-example-promo\b[^"]*"',h,re.I)) == 1,
      'next service': len(re.findall(r'<section\b[^>]*class="[^"]*\bnext-service-module\b[^"]*"',h,re.I)) == 1,
      'order journey': len(re.findall(r'<section\b[^>]*class="[^"]*\bcustomer-order-journey\b[^"]*"',h,re.I)) == 1,
      'identity': len(re.findall(r'<section\b[^>]*class="[^"]*\bidentity-banner\b[^"]*"',h,re.I)) == 1,
      'contact': 'href="contact.html"' in h,
      'sentence-case worked-example heading': '<h2>See how this can work</h2>' in h,
      'sentence-case next-step heading': '<h2>Where this could lead next</h2>' in h,
      'human engagement heading': '<h2>What the engagement looks like</h2>' in h,
      'human promise heading': '<summary>What this service does not promise</summary>' in h,
    }
    for k, ok in checks.items():
        if not ok: errors.append(f'{route}: missing/invalid {k}')
    for legacy in ['<h2>SEE HOW THIS CAN WORK</h2>','<h2>WHERE THIS COULD LEAD NEXT</h2>','<h2>A defined engagement</h2>','<summary>What does House of Carol not promise?</summary>']:
        if legacy in h: errors.append(f'{route}: legacy mechanical heading remains: {legacy}')

for route in EXAMPLES:
    h = (ROOT/route).read_text(encoding='utf-8'); v = visible(h); meta = description_metadata(h)
    for term in FORBIDDEN + ['fictional','synthetic']:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
        if term in meta: errors.append(f'{route}: metadata internal term {term.strip()}')

catalogue = (ROOT/'catalogue.html').read_text(encoding='utf-8')
if 'Seven practical service areas' not in catalogue: errors.append('catalogue.html: corrected problem-led hero eyebrow missing')
if '54 services · seven areas' in catalogue: errors.append('catalogue.html: old 54-service hero emphasis remains')
if 'smallest sensible starting point' not in catalogue: errors.append('catalogue.html: problem-led service-note correction missing')

ai_catalogue = (ROOT/'catalogue-ai-digital.html').read_text(encoding='utf-8')
if '<h3>AI Output Assurance &amp; Red-Team Review</h3>' not in ai_catalogue: errors.append('catalogue-ai-digital.html: HOC-010 canonical name missing')
if '<h3>Independent Document Review</h3>' in ai_catalogue: errors.append('catalogue-ai-digital.html: HOC-010 legacy name remains')

for route in ['catalogue.html','catalogue-research.html','catalogue-church-parish.html','catalogue-charity-public.html']:
    h = (ROOT/route).read_text(encoding='utf-8'); v = visible(h); meta = description_metadata(h)
    for term in ['source universe','house ai-governance kernel','house ai-governance framework','bounded administrative process']:
        if term in v or term in meta: errors.append(f'{route}: remediated internal phrase remains: {term}')
if ' temporal ' in visible((ROOT/'catalogue-church-parish.html').read_text(encoding='utf-8')):
    errors.append('catalogue-church-parish.html: customer-visible temporal language remains')

contact = (ROOT/'contact.html').read_text(encoding='utf-8')
if 'action="https://formspree.io/f/mgvgrgvb"' not in contact: errors.append('contact.html: form endpoint changed unexpectedly')
if 'form-action https://formspree.io' not in contact: errors.append('contact.html: form CSP changed unexpectedly')
for route in ['contact.html','privacy.html','terms.html']:
    h = (ROOT/route).read_text(encoding='utf-8')
    if not re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"|<meta\s+content="noindex,nofollow"\s+name="robots"', h, re.I):
        errors.append(f'{route}: indexing control changed unexpectedly')

if errors:
    print('CUSTOMER EXPERIENCE QA: FAIL', file=sys.stderr)
    for e in errors: print('- ' + e, file=sys.stderr)
    raise SystemExit(1)
print('CUSTOMER EXPERIENCE QA: PASS')
print('Verified 54/54 product pages for customer language, metadata, canonical names, sentence-case headings, service visuals, ordering journey and commercial modules')
print('Verified catalogue remediation, Church-language correction, retained worked examples and unchanged contact/indexing controls')
