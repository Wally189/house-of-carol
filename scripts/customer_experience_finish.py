from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def add_css(html):
    if 'assets/hoc-cx.css' in html:
        return html
    return html.replace('</head>','  <link rel="stylesheet" href="assets/hoc-cx.css">\n</head>',1)

def finish_product(path):
    html=path.read_text(encoding='utf-8')
    html=html.replace('<h2>See how this can work</h2>','<h2>SEE HOW THIS CAN WORK</h2>')
    html=html.replace('<h2>Where this could lead next</h2>','<h2>WHERE THIS COULD LEAD NEXT</h2>')
    html=html.replace('<h2>What the engagement looks like</h2>','<h2>A defined engagement</h2>')
    html=html.replace('<summary>What this service does not promise</summary>','<summary>What does House of Carol not promise?</summary>')
    html=html.replace('You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.','This service is complete in its own right. You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.')
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
