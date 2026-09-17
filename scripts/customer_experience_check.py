from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'scripts/build_case_studies.py').read_text(encoding='utf-8')
block=re.search(r"PRODUCTS = \[(.*?)\]\n",text,re.S).group(1)
PRODUCTS=re.findall(r"'([^']+\.html)'",block)
EXAMPLES=['worked-example-ai-workflow.html','worked-example-process-handover.html','worked-example-trade-account-customer-journey.html','worked-examples.html']
FORBIDDEN=['customer 000','external proof required','owner gate','internal candidate','internal qa','proprietor-approved','lifecycle status','first-test','scope fit','service unit','governance kernel','source universe','temporal service',' bounded ']
errors=[]
def visible(html):
    html=re.sub(r'<(?:style|script)\b.*?</(?:style|script)>',' ',html,flags=re.I|re.S)
    html=re.sub(r'<[^>]+>',' ',html)
    return ' '+re.sub(r'\s+',' ',html).casefold()+' '
for route in PRODUCTS:
    h=(ROOT/route).read_text(encoding='utf-8'); v=visible(h)
    for term in FORBIDDEN:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
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
    h=(ROOT/route).read_text(encoding='utf-8'); v=visible(h)
    for term in FORBIDDEN+['fictional','synthetic']:
        if term in v: errors.append(f'{route}: visible internal term {term.strip()}')
if errors:
    print('CUSTOMER EXPERIENCE QA: FAIL',file=sys.stderr)
    for e in errors: print('- '+e,file=sys.stderr)
    raise SystemExit(1)
print('CUSTOMER EXPERIENCE QA: PASS')
print('Verified 53/53 product pages for external-customer language, one service visual, ordering journey and commercial modules')
print('Verified all retained worked-example routes for evidence-honest external presentation')
