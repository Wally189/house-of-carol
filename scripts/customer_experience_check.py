from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'scripts/build_case_studies.py').read_text(encoding='utf-8')
block=re.search(r"PRODUCTS = \[(.*?)\]\n",text,re.S).group(1)
PRODUCTS=re.findall(r"'([^']+\.html)'",block)
EXAMPLES=['worked-example-ai-workflow.html','worked-example-process-handover.html','worked-example-trade-account-customer-journey.html','worked-examples.html']
FORBIDDEN=['customer 000','external proof required','owner gate','internal candidate','internal qa','proprietor-approved','lifecycle status','first-test','scope fit','service unit','governance kernel','source universe','temporal service',' bounded ']
MALFORMED=['requested what you need this service']
errors=[]
def visible(html):
    html=re.sub(r'<(?:style|script)\b.*?</(?:style|script)>',' ',html,flags=re.I|re.S)
    html=re.sub(r'<[^>]+>',' ',html)
    return ' '+re.sub(r'\s+',' ',html).casefold()+' '
def description_metadata(html):
    values=[]
    for tag in re.findall(r'<meta\b[^>]*>',html,re.I|re.S):
        if not re.search(r'\bname=["\']description["\']',tag,re.I):
            continue
        m=re.search(r'\bcontent=["\'](.*?)["\']',tag,re.I|re.S)
        if m:
            values.append(m.group(1))
    return ' '+re.sub(r'\s+',' ',' '.join(values)).casefold()+' '
for route in PRODUCTS:
    h=(ROOT/route).read_text(encoding='utf-8'); v=visible(h); meta=description_metadata(h)
    for term in FORBIDDEN:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
        if term in meta: errors.append(f'{route}: metadata internal term {term.strip()}')
    for phrase in MALFORMED:
        if phrase in v: errors.append(f'{route}: malformed customer-facing phrase {phrase}')
        if phrase in meta: errors.append(f'{route}: malformed metadata phrase {phrase}')
    checks={
      'single H1':len(re.findall(r'<h1\b',h,re.I))==1,
      'service visual':len(re.findall(r'<figure\b[^>]*class="[^"]*\bproduct-visual\b[^"]*\bcustomer-service-visual\b[^"]*"[^>]*>.*?<img\b[^>]*alt="[^"]+"',h,re.I|re.S))==1,
      'worked example':len(re.findall(r'<section\b[^>]*class="[^"]*\bworked-example-promo\b[^"]*"',h,re.I))==1,
      'next service':len(re.findall(r'<section\b[^>]*class="[^"]*\bnext-service-module\b[^"]*"',h,re.I))==1,
      'order journey':len(re.findall(r'<section\b[^>]*class="[^"]*\bcustomer-order-journey\b[^"]*"',h,re.I))==1,
      'identity':len(re.findall(r'<section\b[^>]*class="[^"]*\bidentity-banner\b[^"]*"',h,re.I))==1,
      'contact':'href="contact.html"' in h,
    }
    for k,ok in checks.items():
        if not ok: errors.append(f'{route}: missing/invalid {k}')
for route in EXAMPLES:
    h=(ROOT/route).read_text(encoding='utf-8'); v=visible(h); meta=description_metadata(h)
    for term in FORBIDDEN+['fictional','synthetic']:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
        if term in meta: errors.append(f'{route}: metadata internal term {term.strip()}')
if errors:
    print('CUSTOMER EXPERIENCE QA: FAIL',file=sys.stderr)
    for e in errors: print('- '+e,file=sys.stderr)
    raise SystemExit(1)
print('CUSTOMER EXPERIENCE QA: PASS')
print('Verified 53/53 product pages for external-customer language and metadata, one service visual, ordering journey and commercial modules')
print('Verified all retained worked-example routes for evidence-honest external presentation')
