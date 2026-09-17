from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

META_REPLACEMENTS=(
    ('first-test research fee','research fee'), ('First-test research fee','Research fee'),
    ('indicative scope band','indicative range'), ('Final price is confirmed after scope fit.','We confirm the exact fee after checking what you need.'),
    ('scope fit','what you need'), ('bounded','focused'), ('Bounded','Focused'),
    ('first-test','initial'), ('First-test','Initial'), ('service unit','service'), ('Service unit','Service'),
    ('governance kernel','governance framework'), ('Governance kernel','Governance framework'),
    ('source universe','source set'), ('Source universe','Source set'), ('temporal','current'), ('Temporal','Current'),
    ('internal QA','quality review'), ('Internal QA','Quality review'), ('proprietor-approved','approved'), ('Proprietor-approved','Approved'),
)

def add_css(html):
    if 'assets/hoc-cx.css' in html:
        return html
    return html.replace('</head>','  <link rel="stylesheet" href="assets/hoc-cx.css">\n</head>',1)

def clean_description_metadata(html):
    def clean_tag(match):
        tag=match.group(0)
        if not re.search(r'\bname=["\']description["\']',tag,re.I):
            return tag
        def clean_content(content_match):
            value=content_match.group(2)
            for old,new in META_REPLACEMENTS:
                value=value.replace(old,new)
            return content_match.group(1)+value+content_match.group(3)
        return re.sub(r'(\bcontent=["\'])(.*?)(["\'])',clean_content,tag,count=1,flags=re.I|re.S)
    return re.sub(r'<meta\b[^>]*>',clean_tag,html,flags=re.I|re.S)

def finish_product(path):
    html=path.read_text(encoding='utf-8')
    html=html.replace('<h2>See how this can work</h2>','<h2>SEE HOW THIS CAN WORK</h2>')
    html=html.replace('<h2>Where this could lead next</h2>','<h2>WHERE THIS COULD LEAD NEXT</h2>')
    html=html.replace('<h2>What the engagement looks like</h2>','<h2>A defined engagement</h2>')
    html=html.replace('<summary>What this service does not promise</summary>','<summary>What does House of Carol not promise?</summary>')
    html=html.replace('You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.','This service is complete in its own right. You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.')
    html=html.replace('the customer, problem, information available and requested what you need this service','the customer, problem, available information and requested scope are suitable for this service')
    html=clean_description_metadata(html)
    html=add_css(html)
    path.write_text(html,encoding='utf-8')

products=[]
for path in ROOT.glob('*.html'):
    text=path.read_text(encoding='utf-8')
    if re.search(r'<body\b[^>]*class="[^"]*\bcanonical-product-page\b',text,re.I) and 'product-fee-text' in text:
        products.append(path)
if len(products)!=53:
    raise SystemExit(f'CX FINISH FAIL: expected 53 products, found {len(products)}')
for p in products: finish_product(p)
for name in ['worked-example-ai-workflow.html','worked-example-process-handover.html','worked-example-trade-account-customer-journey.html','worked-examples.html']:
    p=ROOT/name
    p.write_text(add_css(p.read_text(encoding='utf-8')),encoding='utf-8')
print('PASS: finalised customer-experience presentation while preserving locked commercial QA headings and disclosures')
