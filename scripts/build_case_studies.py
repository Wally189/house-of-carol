from pathlib import Path
from html import unescape
import re

ROOT = Path(__file__).resolve().parents[1]

PRODUCTS = ['ai-data-use-rules-sprint.html',
 'ai-policy-and-sop-implementation-service.html',
 'responsible-ai-workplace-training.html',
 'role-based-ai-skills-workshop.html',
 'ai-leadership-and-management-workshop.html',
 'ai-workflow-opportunity-review.html',
 'ai-workflow-implementation-sprint.html',
 'ai-tool-and-account-governance-review.html',
 'ai-vendor-tool-selection-review.html',
 'independent-document-review.html',
 'ai-operating-model-and-governance-blueprint.html',
 'ai-adoption-support-retainer.html',
 'no-code-ai-automation-implementation.html',
 'business-knowledge-base-and-ai-retrieval-setup.html',
 'process-design-sprint.html',
 'shared-drive-cleanup.html',
 'management-information-and-kpi-setup.html',
 'customer-journey-and-service-operations-review.html',
 'customer-support-knowledge-base-build.html',
 'business-continuity-and-operational-readiness-pack.html',
 'decision-rights-and-governance-review.html',
 'complaints-and-redress-process-design.html',
 'evidence-and-marketing-claim-substantiation-review.html',
 'tender-review.html',
 'tender-readiness-and-bid-evidence-library.html',
 'public-procurement-opportunity-monitoring.html',
 'invoice-to-cash-process-setup.html',
 'cash-flow-and-financial-operations-setup.html',
 'supplier-and-purchasing-process-setup.html',
 'bespoke-organisational-training-design.html',
 'assessment-and-competency-framework-design.html',
 'internal-academy-learning-pathway-design.html',
 'microlearning-and-scenario-assessment-packs.html',
 'research-briefing.html',
 'training-quality-review.html',
 'church-and-parish-grant-funding-research.html',
 'church-grant-application-development-support.html',
 'church-building-funding-and-maintenance-roadmap.html',
 'parish-operations-and-administration-improvement.html',
 'parish-digital-and-ai-governance-starter-service.html',
 'parish-communications-service.html',
 'charity-ai-governance-pack-and-implementation.html',
 'charity-cyber-and-digital-governance-readiness-review.html',
 'charity-governance-and-trustee-information-pack-review.html',
 'public-sector-decision-governance-review.html',
 'committee-board-paper-quality-review.html',
 'public-sector-sop-and-process-modernisation.html',
 'consultation-and-evidence-synthesis-service.html',
 'evidence-based-executive-briefing-service.html',
 'b2b-charity-newsletter-production.html',
 'explainer-and-thought-leadership-production.html',
 'research-monitoring-horizon-scanning-subscription.html',
 'website-completion-sprint.html']

ANGLES = {
'ai-data-use-rules-sprint.html': 'When everyone has an AI shortcut — and nobody agrees where the line is',
'ai-policy-and-sop-implementation-service.html': 'A policy that exists on paper but disappears in the working day',
'responsible-ai-workplace-training.html': 'A team using AI faster than its judgement is developing',
'role-based-ai-skills-workshop.html': 'The same AI training, given to people doing entirely different jobs',
'ai-leadership-and-management-workshop.html': 'Leaders asking for an AI strategy before agreeing what they are trying to improve',
'ai-workflow-opportunity-review.html': 'Five tempting AI ideas, one budget, and no sensible order',
'ai-workflow-implementation-sprint.html': 'A promising AI use case that still depends on one enthusiastic person',
'ai-tool-and-account-governance-review.html': 'Too many AI accounts, too little certainty about who owns what',
'ai-vendor-tool-selection-review.html': 'Three AI tools, six demos and no common basis for choosing',
'independent-document-review.html': 'The board paper is polished. The evidence underneath it is not yet settled.',
'ai-operating-model-and-governance-blueprint.html': 'AI has arrived in pockets; the organisation has not',
'ai-adoption-support-retainer.html': 'After the workshop, the awkward questions start',
'no-code-ai-automation-implementation.html': 'The task is repetitive enough to automate — but messy enough to automate badly',
'business-knowledge-base-and-ai-retrieval-setup.html': 'The answer exists somewhere. Finding the current version is the real job.',
'process-design-sprint.html': 'A process that works only because someone keeps rescuing it',
'shared-drive-cleanup.html': 'A shared drive where nobody deletes anything because nobody knows what is safe',
'management-information-and-kpi-setup.html': 'A dashboard full of numbers and strangely little management information',
'customer-journey-and-service-operations-review.html': 'Every individual step is reasonable. The journey between them is not.',
'customer-support-knowledge-base-build.html': 'The same customer question, answered five slightly different ways',
'business-continuity-and-operational-readiness-pack.html': 'A key person is away — and half the operating model goes with them',
'decision-rights-and-governance-review.html': 'Everyone is involved in the decision; nobody quite owns it',
'complaints-and-redress-process-design.html': 'A complaint process that records the problem but does not reliably resolve it',
'evidence-and-marketing-claim-substantiation-review.html': 'A confident claim meets the awkward question: how do we know?',
'tender-review.html': 'A bid that says all the right things but makes the evaluator work too hard',
'tender-readiness-and-bid-evidence-library.html': 'The tender lands on Friday; the evidence hunt starts from scratch',
'public-procurement-opportunity-monitoring.html': 'The right opportunity appears — three days after anyone notices',
'invoice-to-cash-process-setup.html': 'The invoice was sent. That is not the same as the cash being managed.',
'cash-flow-and-financial-operations-setup.html': 'Revenue looks fine until timing turns into a cash problem',
'supplier-and-purchasing-process-setup.html': 'Buying decisions made one email, exception and urgent request at a time',
'bespoke-organisational-training-design.html': 'A training request that is really a performance problem in disguise',
'assessment-and-competency-framework-design.html': 'People are being assessed, but nobody agrees what good actually looks like',
'internal-academy-learning-pathway-design.html': 'A shelf of courses is not yet a learning pathway',
'microlearning-and-scenario-assessment-packs.html': 'Ten minutes of learning that must change a real decision',
'research-briefing.html': 'The question is simple; the evidence landscape is not',
'training-quality-review.html': 'Training that people enjoy — without clear evidence that it is doing the job',
'church-and-parish-grant-funding-research.html': 'A building need, a crowded funding landscape and no appetite for hopeful form-filling',
'church-grant-application-development-support.html': 'A strong parish project hidden inside a weak application',
'church-building-funding-and-maintenance-roadmap.html': 'Repairs, ambitions and funding routes all competing for the same next decision',
'parish-operations-and-administration-improvement.html': 'Parish administration held together by goodwill and somebody’s memory',
'parish-digital-and-ai-governance-starter-service.html': 'Useful AI experiments arrive before the parish has agreed its boundaries',
'parish-communications-service.html': 'Good parish news, scattered across too many channels and too few hands',
'charity-ai-governance-pack-and-implementation.html': 'A charity wants the benefits of AI without importing a governance headache',
'charity-cyber-and-digital-governance-readiness-review.html': 'Trustees know digital risk matters; the evidence is spread everywhere',
'charity-governance-and-trustee-information-pack-review.html': 'A board pack that informs, but does not yet help trustees govern',
'public-sector-decision-governance-review.html': 'A decision is technically valid but painfully difficult to follow',
'committee-board-paper-quality-review.html': 'The recommendation is on page one. The reason for it is hiding on page nine.',
'public-sector-sop-and-process-modernisation.html': 'A public-service process designed around history rather than the work',
'consultation-and-evidence-synthesis-service.html': 'Hundreds of responses, strong views and one decision that still needs evidence',
'evidence-based-executive-briefing-service.html': 'Too much evidence for a meeting; too little time for a poor synthesis',
'b2b-charity-newsletter-production.html': 'Useful sector intelligence that keeps arriving too late to be useful',
'explainer-and-thought-leadership-production.html': 'Expert knowledge trapped inside prose nobody finishes',
'research-monitoring-horizon-scanning-subscription.html': 'The landscape changes quietly until the decision is suddenly urgent',
'website-completion-sprint.html': 'A website that is 90% built and somehow still nowhere near finished'}

FAMILIES = [
    ('catalogue-operations.html', 'Operations, process & governance', [
        'assets/catalogue-operations-process-progress.webp','assets/operations-sop-process-design.webp','assets/operations-customer-journey.webp','assets/operations-management-information.webp','assets/operations-decision-rights.webp','assets/operations-business-continuity.webp']),
    ('catalogue-ai-digital.html', 'AI, digital & automation', ['assets/catalogue-ai-digital.webp','assets/house-of-carol-knowledge-ideas-books.webp','assets/house-of-carol-generic-still-life-dark.webp','assets/how-it-works-insight-impact.avif']),
    ('catalogue-commercial.html', 'Commercial & financial operations', ['assets/catalogue-commercial-financial-operations.webp','assets/operations-management-information.webp','assets/house-of-carol-generic-still-life-light.webp']),
    ('catalogue-learning.html', 'Learning & organisational capability', ['assets/catalogue-learning-organisational-capability.webp','assets/how-it-works-conversation.avif','assets/house-of-carol-knowledge-ideas-books.webp']),
    ('catalogue-research.html', 'Research, information & communications', ['assets/catalogue-research-information-communications.webp','assets/operations-evidence-claims.webp','assets/house-of-carol-knowledge-ideas-books.webp']),
    ('catalogue-charity-public.html', 'Charity & public-sector services', ['assets/catalogue-charity-public.webp','assets/how-it-works-conversation.avif','assets/house-of-carol-generic-still-life-light.webp']),
    ('catalogue-church-parish.html', 'Church & parish services', ['assets/catalogue-church-parish.webp','assets/house-of-carol-knowledge-ideas-books.webp','assets/house-of-carol-generic-still-life-dark.webp'])]

def strip_tags(fragment):
    fragment = re.sub(r'<[^>]+>', ' ', fragment or '')
    return re.sub(r'\s+', ' ', unescape(fragment)).strip()

def class_text(source, class_name):
    m = re.search(rf'<p\b[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>(.*?)</p>', source, re.I | re.S)
    return strip_tags(m.group(1)) if m else ''

def first_h1(source):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', source, re.I | re.S)
    return strip_tags(m.group(1)) if m else ''

def family_for(source):
    for file_name, label, images in FAMILIES:
        if file_name in source:
            return file_name, label, images
    raise SystemExit('Cannot determine service family for product page')

def card_pairs(source):
    pairs = []
    for block in re.findall(r'<article class="product-card"[^>]*>(.*?)</article>', source, re.I | re.S):
        h = re.search(r'<h3[^>]*>(.*?)</h3>', block, re.I | re.S)
        p = re.search(r'<p[^>]*>(.*?)</p>', block, re.I | re.S)
        if h and p:
            pair = (strip_tags(h.group(1)), strip_tags(p.group(1)))
            if pair not in pairs:
                pairs.append(pair)
    return pairs[:4]

def case_name(route):
    return 'case-study-' + Path(route).stem + '.html'

def nav():
    return '<header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html">HOUSE OF CAROL</a><nav class="main-nav" aria-label="Main navigation"><a href="index.html">Home</a><a href="how-it-works.html">How it works</a><a href="catalogue.html" aria-current="page">Catalogue</a><a href="about.html">About</a><a href="contact.html">Contact</a></nav></div></header>'

def footer():
    return '<footer class="site-footer"><div class="shell footer-layout"><div><div class="footer-brand">HOUSE OF CAROL</div><p>Practical services that help organisations work more productively, efficiently and reliably.</p><p class="footer-identity">Alan W Gallagher trading as House of Carol · Bristol, United Kingdom</p></div><nav class="footer-links" aria-label="Footer navigation"><a href="catalogue.html">Services</a><a href="case-studies.html">Case studies</a><a href="how-it-works.html">How it works</a><a href="about.html">About</a><a href="contact.html">Contact</a><a href="privacy.html">Privacy</a><a href="terms.html">Website terms</a></nav></div></footer>'

def head(title, description):
    return f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#081D2D"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="strict-origin-when-cross-origin"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'none\'; style-src \'self\'; img-src \'self\' data:; font-src \'self\'; connect-src \'none\'; form-action \'none\'; base-uri \'self\'; object-src \'none\'"><link rel="stylesheet" href="assets/hoc-rebuild.css"><link rel="stylesheet" href="assets/hoc-catalogue.css"><link rel="stylesheet" href="assets/hoc-catalogue-remediation.css"><link rel="stylesheet" href="assets/hoc-catalogue-editorial.css?v=20260915-01"><title>{title} — House of Carol</title><meta name="description" content="{description}"></head>'

def situation_copy(index, intro):
    openings = ['The starting point is not a spectacular failure. It is a pattern that keeps costing attention.','Nothing here requires a fictional crisis. The interesting question is whether the working pattern feels familiar.','Imagine the organisation at the point where the work still happens, but confidence in the method has started to thin.','The awkward problems are often the ones that look manageable until they repeat.']
    return openings[index % len(openings)] + (' ' + intro if intro else '')

def build_case(route, index):
    source = (ROOT / route).read_text(encoding='utf-8')
    title = first_h1(source); intro = class_text(source, 'intro'); hook = class_text(source, 'product-hook')
    audience = re.sub(r'^For:\s*', '', class_text(source, 'product-audience'), flags=re.I)
    scope = class_text(source, 'product-scope-line'); trust = class_text(source, 'product-trust-line')
    family_file, family_label, images = family_for(source); image = images[index % len(images)]
    cards = card_pairs(source)
    fallbacks = [('Understand the starting point','Use the agreed evidence and customer context to establish what is actually happening.'),('Work within a defined boundary',scope or 'Keep the engagement tied to the named service boundary.'),('Hand back something usable',trust or 'Leave the customer with a clear, bounded output rather than an open-ended programme.')]
    for fallback in fallbacks:
        if len(cards) >= 3: break
        if fallback not in cards: cards.append(fallback)
    cards_html = ''.join(f'<article class="case-output"><h3>{h}</h3><p>{p}</p></article>' for h,p in cards)
    angle = ANGLES[route]; body_class = 'case-study-page case-layout-' + str((index % 4) + 1)
    situation = situation_copy(index, intro); description = ('Illustrative ' + title + ' case study: ' + angle)[:154].rstrip(' ,.;:-') + '.'
    work_heading = 'Find the real constraint before prescribing the fix.' if index % 2 == 0 else 'Make the boundary useful, then do the work inside it.'
    return f'''{head(title + ' — illustrative case study', description)}<body class="{body_class}"><a class="skip" href="#main">Skip to content</a>{nav()}<main id="main"><nav class="catalogue-breadcrumbs shell" aria-label="Breadcrumb"><a href="index.html">Home</a> → <a href="catalogue.html">Catalogue</a> → <a href="case-studies.html">Case studies</a> → <span aria-current="page">{title}</span></nav><section class="case-study-hero"><div class="shell case-study-hero-grid"><div class="case-study-hero-copy"><p class="eyebrow">Illustrative case study · {family_label}</p><h1>{angle}</h1><div class="claret-rule"></div><p class="lede">{hook or title}</p><p class="case-disclosure"><strong>Composite illustration, not a real customer or claimed result.</strong> It shows the shape of the problem, the judgement and the work without pretending that invented evidence is proof.</p><div class="catalogue-hero-actions"><a class="button" href="{route}">View the {title} service</a><a class="text-link" href="case-studies.html">Browse all case studies →</a></div></div><figure class="case-study-hero-visual"><img src="{image}" alt="Illustrative workspace for {family_label}"></figure></div></section><section class="section case-story"><div class="shell case-story-grid"><div><p class="eyebrow">The situation</p><h2>What is actually going wrong?</h2></div><div class="case-prose"><p>{situation}</p><p><strong>Who this is for:</strong> {audience or 'an organisation facing the problem described by the service.'}</p></div></div></section><section class="section case-decision"><div class="shell"><div class="worked-examples-head"><div><p class="eyebrow">The work</p><h2>{work_heading}</h2></div><p>{scope or 'The engagement stays inside the named product boundary and uses the evidence available to make the next decision clearer.'}</p></div><div class="case-output-grid">{cards_html}</div></div></section><section class="section case-judgement"><div class="shell case-story-grid"><div><p class="eyebrow">The judgement</p><h2>What would make this worth doing?</h2></div><div class="case-prose"><p>{trust or 'The useful result is a bounded improvement that can be understood, checked and used by the customer.'}</p><p>The case study deliberately stops before inventing savings, percentages, testimonials or a triumphant after-picture. Those claims belong to real evidence, not creative writing.</p></div></div></section><section class="section case-next"><div class="shell next-service-panel"><p class="eyebrow">The actual service</p><h2>{title}</h2><p>If this scenario resembles the problem you are trying to solve, read the service page for the current scope, price, boundaries and what happens next.</p><div class="next-service-links"><a href="{route}">View the service →</a><a href="{family_file}">Explore {family_label} →</a><a href="catalogue.html">Back to the full catalogue →</a></div></div></section></main>{footer()}</body></html>'''

def inject_product_link(route):
    path = ROOT / route; source = path.read_text(encoding='utf-8'); case = case_name(route)
    if f'href="{case}"' in source: return
    marker = '<nav aria-label="Service navigation" class="service-context-nav">'
    if marker not in source: raise SystemExit(f'Service navigation marker missing from {route}')
    title = first_h1(source)
    promo = f'<section class="product-section product-case-study-route"><div class="shell next-service-panel"><p class="eyebrow">See the service in context</p><h2>A separate illustrative case study for {title}</h2><p>See the kind of problem this service is designed to tackle, without confusing a composite scenario with customer proof.</p><div class="next-service-links"><a href="{case}">Read the illustrative case study →</a><a href="case-studies.html">Browse all case studies →</a></div></div></section>'
    path.write_text(source.replace(marker, promo + marker, 1), encoding='utf-8')

def build_index(records):
    family_sections = []
    for family_file, family_label, images in FAMILIES:
        group = [r for r in records if r['family_file'] == family_file]
        if not group: continue
        cards = ''.join(f'<article class="case-study-card"><p class="eyebrow">{r["title"]}</p><h3><a class="case-study-link" href="{r["case"]}">{r["angle"]}</a></h3><p>{r["hook"] or "A product-specific composite scenario."}</p><a class="case-product-link" href="{r["route"]}">View service →</a></article>' for r in group)
        family_sections.append(f'<section class="section case-family"><div class="shell"><div class="case-family-head"><div><p class="eyebrow">{len(group)} case studies</p><h2>{family_label}</h2><p>Each page is a separate composite scenario tied to one current service.</p></div><figure><img src="{images[0]}" alt="Illustrative workspace for {family_label}"></figure></div><div class="case-index-grid">{cards}</div></div></section>')
    return f'''{head('Illustrative case studies','Fifty-three product-specific illustrative House of Carol case studies, clearly separated from real customer evidence.')}<body class="case-study-index-page"><a class="skip" href="#main">Skip to content</a>{nav()}<main id="main"><section class="catalogue-hero case-index-hero"><div class="shell"><div class="catalogue-hero-grid"><div class="catalogue-hero-copy"><p class="eyebrow">53 services · 53 separate illustrations</p><h1>See the problem before you buy the answer.</h1><div class="claret-rule"></div><p class="lede">Every current House of Carol service has its own illustrative case study. They are not testimonials and they are not invented customer results. They are a clearer way to show the judgement, boundary and practical shape of the work.</p><p class="service-note">Real proof will be labelled as real proof. Until then, these pages do something more honest: they let you inspect the thinking.</p><div class="catalogue-hero-actions"><a class="button" href="catalogue.html">Browse services</a><a class="text-link" href="#case-families">Browse all 53 case studies →</a></div></div><figure class="catalogue-hero-visual"><img src="assets/house-of-carol-knowledge-ideas-books.webp" alt="Books, notes and working materials representing ideas being examined"></figure></div></div></section><div id="case-families">{"".join(family_sections)}</div></main>{footer()}</body></html>'''

records = []
for index, route in enumerate(PRODUCTS):
    source = (ROOT / route).read_text(encoding='utf-8'); family_file, family_label, images = family_for(source)
    title = first_h1(source); hook = class_text(source, 'product-hook'); case = case_name(route)
    (ROOT / case).write_text(build_case(route, index), encoding='utf-8'); inject_product_link(route)
    records.append({'route':route,'case':case,'title':title,'hook':hook,'angle':ANGLES[route],'family_file':family_file,'family_label':family_label})
(ROOT / 'case-studies.html').write_text(build_index(records), encoding='utf-8')
print(f'PASS: generated {len(records)} product-specific illustrative case-study pages and linked all product pages')
