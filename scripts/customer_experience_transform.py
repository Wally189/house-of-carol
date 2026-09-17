from pathlib import Path
from html import escape, unescape
import json, re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
HOOKS = json.loads((DATA / 'cx_hooks.json').read_text(encoding='utf-8'))
PRICES = json.loads((DATA / 'cx_prices.json').read_text(encoding='utf-8'))

ASSET_GROUPS = {
    'assets/catalogue-ai-digital.webp': {'ai-data-use-rules-sprint.html','ai-policy-and-sop-implementation-service.html','ai-workflow-opportunity-review.html','ai-workflow-implementation-sprint.html','ai-tool-and-account-governance-review.html','ai-vendor-tool-selection-review.html','no-code-ai-automation-implementation.html','website-completion-sprint.html'},
    'assets/how-it-works-conversation.avif': {'responsible-ai-workplace-training.html','role-based-ai-skills-workshop.html','ai-adoption-support-retainer.html'},
    'assets/how-it-works-insight-impact.avif': {'ai-leadership-and-management-workshop.html','ai-operating-model-and-governance-blueprint.html'},
    'assets/operations-evidence-claims.webp': {'independent-document-review.html','evidence-and-marketing-claim-substantiation-review.html'},
    'assets/house-of-carol-knowledge-ideas-books.webp': {'business-knowledge-base-and-ai-retrieval-setup.html'},
    'assets/hoc015-deliverables-preview.webp': {'process-design-sprint.html'},
    'assets/operations-document-control.webp': {'shared-drive-cleanup.html'},
    'assets/operations-management-information.webp': {'management-information-and-kpi-setup.html'},
    'assets/operations-customer-journey.webp': {'customer-journey-and-service-operations-review.html'},
    'assets/operations-support-knowledge-base.webp': {'customer-support-knowledge-base-build.html'},
    'assets/operations-business-continuity.webp': {'business-continuity-and-operational-readiness-pack.html'},
    'assets/operations-decision-rights.webp': {'decision-rights-and-governance-review.html'},
    'assets/operations-complaints-redress.webp': {'complaints-and-redress-process-design.html'},
    'assets/catalogue-commercial-financial-operations.webp': {'tender-review.html','tender-readiness-and-bid-evidence-library.html','public-procurement-opportunity-monitoring.html','invoice-to-cash-process-setup.html','cash-flow-and-financial-operations-setup.html','supplier-and-purchasing-process-setup.html'},
    'assets/catalogue-learning-organisational-capability.webp': {'bespoke-organisational-training-design.html','assessment-and-competency-framework-design.html','internal-academy-learning-pathway-design.html','microlearning-and-scenario-assessment-packs.html','training-quality-review.html'},
    'assets/catalogue-research-information-communications.webp': {'research-briefing.html','evidence-based-executive-briefing-service.html','b2b-charity-newsletter-production.html','explainer-and-thought-leadership-production.html','research-monitoring-horizon-scanning-subscription.html'},
    'assets/catalogue-church-parish.webp': {'church-and-parish-grant-funding-research.html','church-grant-application-development-support.html','church-building-funding-and-maintenance-roadmap.html','parish-operations-and-administration-improvement.html','parish-digital-and-ai-governance-starter-service.html','parish-communications-service.html'},
    'assets/catalogue-charity-public.webp': {'charity-ai-governance-pack-and-implementation.html','charity-cyber-and-digital-governance-readiness-review.html','charity-governance-and-trustee-information-pack-review.html','public-sector-decision-governance-review.html','committee-board-paper-quality-review.html','public-sector-sop-and-process-modernisation.html','consultation-and-evidence-synthesis-service.html'},
}
ROUTE_ASSET = {route: asset for asset, routes in ASSET_GROUPS.items() for route in routes}

ORDER_JOURNEY = '''<section class="product-section alt customer-order-journey"><div class="shell"><div class="product-section-heading"><p class="eyebrow">FROM INTEREST TO A CLEAR DECISION</p><h2>How to get started</h2><p class="section-lead">Start with the problem, not a purchase decision. We will check whether this service fits before anything is agreed.</p></div><div class="product-section-body"><div class="deliverable-groups generic-deliverables customer-order-steps"><article class="product-card"><h3>1. Tell us what is happening</h3><p>Share the problem you are trying to solve, what you already have and any deadline or constraint that matters.</p></article><article class="product-card"><h3>2. We check the fit</h3><p>We check the scope, the information we would need, the fee and whether this is genuinely the right service. If it is not, we will say so.</p></article><article class="product-card"><h3>3. You decide with the facts clear</h3><p>Nothing starts until you know what is included, what is not, what you need to provide and what happens next.</p></article></div><p class="customer-order-reassurance">There is no pressure to add another service. The useful next step is simply to decide whether this one solves the problem in front of you.</p></div></div></section>'''

VISIBLE_REPLACEMENTS = (
    ('first-test research fee', 'research fee'), ('First-test research fee', 'Research fee'),
    ('indicative scope band', 'indicative range'), ('Final price is confirmed after scope fit.', 'We confirm the exact fee after checking what you need.'),
    ('scope fit', 'what you need'), ('bounded', 'focused'), ('Bounded', 'Focused'),
    ('first-test', 'initial'), ('First-test', 'Initial'), ('service unit', 'service'), ('Service unit', 'Service'),
    ('source universe', 'source set'), ('Source universe', 'Source set'),
    ('internal QA', 'quality review'), ('Internal QA', 'Quality review'), ('proprietor-approved', 'approved'), ('Proprietor-approved', 'Approved'),
)

def fail(msg): raise SystemExit('CUSTOMER EXPERIENCE BUILD FAIL: ' + msg)

def plain(s):
    return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()

def replace_visible(html):
    parts = re.split(r'(<[^>]+>)', html)
    for i in range(0, len(parts), 2):
        for old,new in VISIBLE_REPLACEMENTS:
            parts[i] = parts[i].replace(old,new)
    return ''.join(parts)

def replace_class_inner(html, class_name, new_inner):
    pattern = re.compile(r'(<(?P<tag>\w+)\b[^>]*class="[^"]*\b'+re.escape(class_name)+r'\b[^"]*"[^>]*>)(.*?)(</(?P=tag)>)', re.I|re.S)
    return pattern.sub(lambda m: m.group(1)+new_inner+m.group(4), html, count=1)

def section_bounds(html, class_name=None, heading=None):
    if class_name:
        hit = re.search(r'<section\b[^>]*class="[^"]*\b'+re.escape(class_name)+r'\b[^"]*"[^>]*>', html, re.I)
        if not hit: fail(f'missing section class {class_name}')
        start=hit.start()
    else:
        pos=html.find(f'<h2>{heading}</h2>')
        if pos<0: fail(f'missing heading {heading}')
        start=html.rfind('<section',0,pos)
    end=html.find('</section>',start)
    if start<0 or end<0: fail('section bounds unavailable')
    return start,end+len('</section>')

def product_title(html):
    m=re.search(r'<h1\b[^>]*>(.*?)</h1>',html,re.I|re.S)
    return plain(m.group(1)) if m else ''

def add_visual(route, html):
    if 'customer-service-visual' in html: return html
    asset=ROUTE_ASSET.get(route)
    if not asset: fail(f'{route}: no service visual mapping')
    title=product_title(html)
    alt=f'Working materials representing {title}.'
    figure=f'<figure class="product-visual customer-service-visual"><img src="{asset}" alt="{escape(alt)}" width="1200" height="800" loading="lazy"><figcaption>{escape(alt)}</figcaption></figure>'
    start,end=section_bounds(html, heading='What you will receive')
    block=html[start:end]
    body=re.search(r'<div class="product-section-body">',block)
    if not body: fail(f'{route}: deliverables body missing')
    p=start+body.end()
    return html[:p]+figure+html[p:]

def humanise_worked_example(html):
    html=html.replace('<h2>SEE HOW THIS CAN WORK</h2>','<h2>See how this can work</h2>')
    html=html.replace('<strong>A clearer target state:</strong>','<strong>A clearer result:</strong>')
    html=html.replace('<strong>The customer could receive:</strong>','<strong>What you could receive:</strong>')
    html=html.replace('<span>House of Carol examines</span>','<span>What we look at</span>')
    html=html.replace('<span>Clearer state</span>','<span>Clearer result</span>')
    html=html.replace('<span>Customer receives</span>','<span>What you receive</span>')
    html=re.sub(r'<p>House of Carol would examine the agreed current position,.*?wider transformation\.</p>', '<p>We would start with what is happening now and the information already available, then work through the service described on this page. If the problem needs a different route, we would say so before broadening the work.</p>', html, count=1, flags=re.S)
    html=re.sub(r'<div><span>What we look at</span><p>.*?</p></div>', '<div><span>What we look at</span><p>What is happening now, the information available and the result you need.</p></div>', html, count=1, flags=re.S)
    return html

def humanise_next_steps(html):
    html=html.replace('<h2>WHERE THIS COULD LEAD NEXT</h2>','<h2>Where this could lead next</h2>')
    html=html.replace('This service is complete in its own right. If the work identifies a separate problem worth solving, these are the most likely next steps.', 'You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.')
    return html

def add_order_journey(route, html):
    if 'customer-order-journey' in html: return html
    start,end=section_bounds(html,class_name='disclosures-section')
    return html[:end]+ORDER_JOURNEY+html[end:]

def transform_product(path):
    route=path.name; html=path.read_text(encoding='utf-8')
    if route in HOOKS: html=replace_class_inner(html,'product-hook',HOOKS[route])
    if route in PRICES: html=replace_class_inner(html,'product-price',PRICES[route])
    html=humanise_worked_example(html)
    html=humanise_next_steps(html)
    html=html.replace('<h2>A defined engagement</h2>','<h2>What the engagement looks like</h2>')
    html=html.replace('<summary>What does House of Carol not promise?</summary>','<summary>What this service does not promise</summary>')
    html=replace_visible(html)
    html=add_visual(route,html)
    html=add_order_journey(route,html)
    path.write_text(html,encoding='utf-8')

def transform_examples():
    replacements={
      'worked-example-ai-workflow.html': [('Worked example: a bounded AI workflow','Worked example: a focused AI workflow'),('From “could AI help?” to one bounded human-operated workflow','From “could AI help?” to one practical human-operated workflow'),('What House of Carol would look at','What we would look at')],
      'worked-example-process-handover.html': [('What House of Carol would look at','What we would look at')],
      'worked-example-trade-account-customer-journey.html': [('What House of Carol would look at','What we would look at')],
      'worked-examples.html': [('From an AI idea to a bounded working method','From an AI idea to a practical working method')],
    }
    for name,pairs in replacements.items():
      path=ROOT/name; html=path.read_text(encoding='utf-8')
      for old,new in pairs: html=html.replace(old,new)
      html=replace_visible(html)
      if name=='worked-example-trade-account-customer-journey.html' and 'customer-service-visual' not in html:
        marker='<div class="example-brief-grid">'
        fig='<figure class="product-visual customer-service-visual"><img src="assets/operations-customer-journey.webp" alt="Customer-journey mapping and service-operation materials." width="1200" height="800" loading="lazy"><figcaption>Customer-journey mapping and service-operation materials.</figcaption></figure>'
        html=html.replace(marker,fig+marker,1)
      path.write_text(html,encoding='utf-8')

products=[]
for path in ROOT.glob('*.html'):
    text=path.read_text(encoding='utf-8')
    if re.search(r'<body\b[^>]*class="[^"]*\bcanonical-product-page\b', text, re.I) and re.search(r'class="[^"]*\bproduct-price\b[^"]*\bproduct-fee-text\b', text, re.I):
        products.append(path)
if len(products)!=53: fail(f'expected 53 product pages after commercial build, found {len(products)}')
if set(ROUTE_ASSET)!={p.name for p in products}: fail('service visual map does not match 53 current product routes')
for path in products: transform_product(path)
transform_examples()
print('PASS: applied customer-experience journey, language, pricing presentation and service visuals across 53 products and retained worked examples')
