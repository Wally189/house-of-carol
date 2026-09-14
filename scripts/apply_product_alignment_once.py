from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding='utf-8')


def write(name, text):
    (ROOT / name).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one occurrence, found {count}')
    return text.replace(old, new, 1)


def normalise_head(text, old_css):
    text = text.replace(old_css, 'assets/hoc-service.css?v=20260912-corrective2')
    if '<meta name="theme-color"' not in text:
        text = replace_once(
            text,
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n  <meta name="theme-color" content="#081D2D">',
            'theme-color insertion',
        )
    text = text.replace('<meta name="theme-color" content="#081d2d">', '<meta name="theme-color" content="#081D2D">')
    return text

# HOC-001
p = 'ai-data-use-rules-sprint.html'
t = normalise_head(read(p), 'assets/hoc-service.css?v=20260910-product-standard2')
t = replace_once(
    t,
    '<dt>Pricing</dt><dd>£1,250 fixed fee</dd>\n          <dt>Planned delivery</dt>',
    '<dt>Pricing</dt><dd>£1,250 fixed fee</dd>\n          <dt>Scope</dt><dd>The standard Sprint covers 3–5 representative low- or moderate-risk workflows, a 45-minute discovery session, a 45-minute team briefing and five work-like scenario checks.</dd>\n          <dt>Planned delivery</dt>',
    'HOC-001 scope fact',
)
t = replace_once(
    t,
    '<summary>Is this the right service for our organisation?</summary>\n            <div class="hoc-accordion-panel">',
    '<summary>Is this the right service?</summary>\n            <div class="hoc-accordion-panel">\n              <p><strong>Is this the right service for our organisation?</strong></p>',
    'HOC-001 fit disclosure',
)
t = replace_once(
    t,
    '          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    '          </details>\n\n          <details class="hoc-accordion">\n            <summary>What does House of Carol not promise?</summary>\n            <div class="hoc-accordion-panel">\n              <p>The Sprint does not decide legal permissibility for your organisation. It turns the requirements and decisions your organisation is competent to approve into a practical rule people can use.</p>\n            </div>\n          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    'HOC-001 claim disclosure',
)
write(p, t)

# HOC-004
p = 'role-based-ai-skills-workshop.html'
t = normalise_head(read(p), 'assets/hoc-service.css?v=20260911-hoc004-role1')
t = replace_once(t, '<section class="product-hero">', '<section class="product-hero standard-product-hero">', 'HOC-004 hero class')
t = replace_once(
    t,
    '      <p class="intro">House of Carol builds one practical workshop around a defined team or role family and three recurring workflows, so participants practise the work rather than sit through another general AI presentation.</p>\n      <div class="product-price">',
    '      <p class="intro">House of Carol builds one practical workshop around a defined team or role family and three recurring workflows, so participants practise the work rather than sit through another general AI presentation.</p>\n      <p class="product-audience"><strong>The workshop is designed for teams where the AI basics are no longer the main problem.</strong></p>\n      <div class="product-price product-fee-text">',
    'HOC-004 audience and price class',
)
t = replace_once(
    t,
    '      <h2>Does this sound familiar?</h2>\n      <p class="section-lead">The workshop is designed for teams where the AI basics are no longer the main problem.</p>',
    '      <h2>What changes</h2>\n      <p class="section-lead"><strong>Does this sound familiar?</strong></p>\n      <p class="section-lead">The workshop is designed for teams where the AI basics are no longer the main problem.</p>',
    'HOC-004 what changes',
)
t = replace_once(
    t,
    '      <h2>What you will leave with</h2>\n      <p class="section-lead">A practical role-based learning unit built around work your team recognises.</p>\n      <div class="deliverable-groups">',
    '      <h2>What you will receive</h2>\n      <p class="section-lead"><strong>What you will leave with</strong></p>\n      <p class="section-lead">A practical role-based learning unit built around work your team recognises.</p>\n      <div class="deliverable-groups generic-deliverables">',
    'HOC-004 deliverables',
)
t = replace_once(
    t,
    '      <h2>A bounded £1,250 workshop</h2>\n      <p class="section-lead">The standard service is deliberately one defined learning unit:</p>',
    '      <h2>A defined engagement</h2>\n      <p class="section-lead"><strong>A bounded £1,250 workshop</strong></p>\n      <dl class="service-facts standard-service-facts">\n        <dt>Service type</dt><dd>Role-Based AI Skills Workshop</dd>\n        <dt>Delivery</dt><dd>One three-hour live remote workshop.</dd>\n        <dt>Pricing</dt><dd>£1,250 fixed.</dd>\n        <dt>Scope</dt><dd>One role family or coherent team. Up to 12 adult participants. Three representative workflows.</dd>\n      </dl>\n      <p class="section-lead">The standard service is deliberately one defined learning unit:</p>',
    'HOC-004 defined engagement',
)
t = replace_once(
    t,
    '<summary>What do you need from us?</summary>\n          <div class="hoc-accordion-panel">',
    '<summary>What needs to be in place?</summary>\n          <div class="hoc-accordion-panel">\n            <p><strong>What do you need from us?</strong></p>',
    'HOC-004 requirements',
)
t = replace_once(
    t,
    '<summary>What is outside the standard workshop?</summary>\n          <div class="hoc-accordion-panel">',
    '<summary>What is outside the scope?</summary>\n          <div class="hoc-accordion-panel">\n            <p><strong>What is outside the standard workshop?</strong></p>',
    'HOC-004 exclusions',
)
t = replace_once(
    t,
    '<summary>Is this the right workshop for our team?</summary>\n          <div class="hoc-accordion-panel">',
    '<summary>Is this the right service?</summary>\n          <div class="hoc-accordion-panel">\n            <p><strong>Is this the right workshop for our team?</strong></p>',
    'HOC-004 fit',
)
t = replace_once(
    t,
    '        </details>\n      </div>\n    </div>\n  </section>\n\n  <section class="product-section alt">',
    '        </details>\n\n        <details class="hoc-accordion">\n          <summary>What does House of Carol not promise?</summary>\n          <div class="hoc-accordion-panel">\n            <p>This is a workshop application check, not an accredited qualification or professional competence certificate.</p>\n          </div>\n        </details>\n      </div>\n    </div>\n  </section>\n\n  <section class="product-section alt">',
    'HOC-004 claim disclosure',
)
write(p, t)

# HOC-006
p = 'ai-workflow-opportunity-review.html'
t = normalise_head(read(p), 'assets/hoc-service.css?v=20260910-product-standard2')
t = replace_once(
    t,
    '<summary>Is this the right review for our organisation?</summary>\n            <div class="hoc-accordion-panel">',
    '<summary>Is this the right service?</summary>\n            <div class="hoc-accordion-panel">\n              <p><strong>Is this the right review for our organisation?</strong></p>',
    'HOC-006 fit',
)
t = replace_once(
    t,
    '          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    '          </details>\n\n          <details class="hoc-accordion">\n            <summary>What does House of Carol not promise?</summary>\n            <div class="hoc-accordion-panel">\n              <p>It does not guarantee time savings, productivity gains, revenue impact or implementation feasibility.</p>\n            </div>\n          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    'HOC-006 claim disclosure',
)
write(p, t)

# HOC-007
p = 'ai-workflow-implementation-sprint.html'
t = normalise_head(read(p), 'assets/hoc-service.css?v=20260910-product-standard2')
t = replace_once(
    t,
    '        <h2>A defined implementation</h2>\n        <dl class="service-facts standard-service-facts">',
    '        <h2>A defined engagement</h2>\n        <p class="section-lead"><strong>A defined implementation</strong></p>\n        <dl class="service-facts standard-service-facts">',
    'HOC-007 defined engagement',
)
t = replace_once(
    t,
    '<summary>Is this the right service for our organisation?</summary>\n            <div class="hoc-accordion-panel">',
    '<summary>Is this the right service?</summary>\n            <div class="hoc-accordion-panel">\n              <p><strong>Is this the right service for our organisation?</strong></p>',
    'HOC-007 fit',
)
t = replace_once(
    t,
    '          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    '          </details>\n\n          <details class="hoc-accordion">\n            <summary>What does House of Carol not promise?</summary>\n            <div class="hoc-accordion-panel">\n              <p>The sprint does not promise a percentage time saving, accuracy rate, revenue gain or return on investment. Any benefit has to be observed in real use rather than invented in advance.</p>\n            </div>\n          </details>\n        </div>\n      </div>\n    </section>\n\n    <section class="product-section alt">',
    'HOC-007 claim disclosure',
)
write(p, t)

# HOC-064
p = 'website-completion-sprint.html'
t = normalise_head(read(p), 'assets/hoc-service.css?v=20260911-hoc064-review1')
t = replace_once(t, '<section class="product-hero"><div class="shell">', '<section class="product-hero standard-product-hero"><div class="shell">', 'HOC-064 hero class')
t = replace_once(
    t,
    '    <p class="intro">House of Carol takes one existing website that is substantially built and worth preserving, works out exactly what is preventing it from being properly complete, fixes the agreed final-mile issues and tests the resulting site against a clear completion standard.</p>\n    <div class="product-price">',
    '    <p class="intro">House of Carol takes one existing website that is substantially built and worth preserving, works out exactly what is preventing it from being properly complete, fixes the agreed final-mile issues and tests the resulting site against a clear completion standard.</p>\n    <p class="product-audience"><strong>This sprint is designed for an owner-managed or small service organisation when:</strong></p>\n    <div class="product-price product-fee-text">',
    'HOC-064 audience/price',
)
t = replace_once(
    t,
    '    <p class="product-turnaround">Normally planned for completion within five working days once the agreed access, content and decisions are available. Customer delay pauses the clock.</p>\n    <div class="actions">',
    '    <p class="product-turnaround">Normally planned for completion within five working days once the agreed access, content and decisions are available. Customer delay pauses the clock.</p>\n    <p class="product-trust-line"><strong>No guaranteed rankings, leads, conversion or imaginary savings.</strong></p>\n    <div class="actions">',
    'HOC-064 trust line',
)
t = replace_once(t, '    <h2>Does this sound familiar?</h2>', '    <h2>What changes</h2>\n    <p class="section-lead"><strong>Does this sound familiar?</strong></p>', 'HOC-064 what changes')
t = replace_once(
    t,
    '    <h2>What you get</h2>\n    <p class="section-lead">For one existing website:</p>\n    <div class="deliverable-groups">',
    '    <h2>What you will receive</h2>\n    <p class="section-lead"><strong>What you get</strong></p>\n    <p class="section-lead">For one existing website:</p>\n    <div class="deliverable-groups generic-deliverables">',
    'HOC-064 deliverables',
)
t = replace_once(
    t,
    '  </div></section>\n\n  <section class="product-section disclosures-section">',
    '  </div></section>\n\n  <section class="product-section alt"><div class="shell bounded-review">\n    <h2>A defined engagement</h2>\n    <dl class="service-facts standard-service-facts">\n      <dt>Service type</dt><dd>Website Completion Sprint</dd>\n      <dt>Delivery</dt><dd>The completion job is treated as one accountable piece of work from current-state takeover through implementation, QA and handover rather than being split into a series of unrelated fixes.</dd>\n      <dt>Pricing</dt><dd>One existing website. Up to 10 agreed public pages/URLs. £1,250 fixed.</dd>\n      <dt>Scope</dt><dd>One existing website · up to 10 agreed public pages/URLs · one primary enquiry/contact journey · one defined completion scope · one pre-release QA cycle · one bounded correction cycle</dd>\n      <dt>Timing</dt><dd>Normally planned for completion within five working days once the agreed access, content and decisions are available. Customer delay pauses the clock.</dd>\n    </dl>\n  </div></section>\n\n  <section class="product-section disclosures-section">',
    'HOC-064 defined engagement insertion',
)
t = replace_once(t, '<details class="hoc-accordion"><summary>What we need from you</summary><div class="hoc-accordion-panel">', '<details class="hoc-accordion"><summary>What needs to be in place?</summary><div class="hoc-accordion-panel"><p><strong>What we need from you</strong></p>', 'HOC-064 requirements')
t = replace_once(t, '<details class="hoc-accordion"><summary>Good fit</summary><div class="hoc-accordion-panel">', '<details class="hoc-accordion"><summary>Is this the right service?</summary><div class="hoc-accordion-panel"><p><strong>Good fit</strong></p>', 'HOC-064 fit')
t = replace_once(t, '<details class="hoc-accordion"><summary>Probably not a good fit</summary><div class="hoc-accordion-panel">', '<details class="hoc-accordion"><summary>What is outside the scope?</summary><div class="hoc-accordion-panel"><p><strong>Probably not a good fit</strong></p>', 'HOC-064 exclusions')
t = replace_once(
    t,
    '    <details class="hoc-accordion"><summary>Price</summary><div class="hoc-accordion-panel"><p>One existing website. Up to 10 agreed public pages/URLs. £1,250 fixed.</p><p>No open-ended consulting meter.</p><p>No charge for inventing more deliverables.</p><p>No guaranteed rankings, leads, conversion or imaginary savings.</p><p>No attempt to turn a simple fix into a larger engagement.</p></div></details>\n  </div></div></section>',
    '    <details class="hoc-accordion"><summary>Price</summary><div class="hoc-accordion-panel"><p>One existing website. Up to 10 agreed public pages/URLs. £1,250 fixed.</p><p>No open-ended consulting meter.</p><p>No charge for inventing more deliverables.</p><p>No guaranteed rankings, leads, conversion or imaginary savings.</p><p>No attempt to turn a simple fix into a larger engagement.</p></div></details>\n    <details class="hoc-accordion"><summary>What does House of Carol not promise?</summary><div class="hoc-accordion-panel"><p>No guaranteed rankings, leads, conversion or imaginary savings.</p><p>No attempt to turn a simple fix into a larger engagement.</p></div></details>\n  </div></div></section>',
    'HOC-064 claim disclosure',
)
write(p, t)

# Whole-estate QA: all 53 product pages are now one canonical structure.
p = 'scripts/product_page_standardisation_check.py'
t = read(p)
t = re.sub(
    r'# Separately accepted non-Operations reference pages retain their source-bound\n# information architecture\. HOC-015 through HOC-023 now share one structural\n# Operations contract and are therefore deliberately not exempted here\.\nREFERENCE_PAGES = \{.*?\}\n\nOPERATIONS_PAGES = \{.*?\}\n',
    '# All 53 current DEVELOP product pages use one canonical structural contract.\nREFERENCE_PAGES = set()\n\nCANONICAL_PAGES = set(EXPECTED_PRICES)\n',
    t,
    flags=re.S,
)
t = t.replace('OPERATIONS_PAGES', 'CANONICAL_PAGES')
t = t.replace('operations_snapshots', 'canonical_snapshots')
t = t.replace('Operations canonical-contract failure', 'canonical-contract failure')
t = t.replace('Operations canonical cardinality', 'canonical cardinality')
t = t.replace('Operations module-order marker missing', 'canonical module-order marker missing')
t = t.replace('Operations module order invalid', 'canonical module order invalid')
t = t.replace('Operations canonical snapshots missing', 'Canonical snapshots missing')
t = t.replace('Operations canonical reference page has unreadable global shell', 'Canonical reference page has unreadable global shell')
t = t.replace('Operations global header differs from canonical reference', 'global header differs from canonical reference')
t = t.replace('Operations global footer differs from canonical reference', 'global footer differs from canonical reference')
t = t.replace('Operations stylesheet list differs from canonical reference', 'stylesheet list differs from canonical reference')
t = t.replace('Operations CSP differs from canonical reference', 'CSP differs from canonical reference')
old_anchor = '''        expected_anchor = f"catalogue-operations.html#{offer_id.lower()}"
        breadcrumb = extract_class_block(html, "nav", "service-breadcrumbs")
        context_nav = extract_class_block(html, "nav", "service-context-nav")
        if not breadcrumb or f'href="{expected_anchor}"' not in breadcrumb:
            errors.append(f"{offer_id} {href}: breadcrumb does not point to {expected_anchor}")
        if not context_nav:
            errors.append(f"{offer_id} {href}: context navigation block unreadable")
        else:
            nav_hrefs = re.findall(r'<a\\s+href="([^\"]+)"', context_nav, re.I)
            expected_hrefs = [expected_anchor, "catalogue.html", "index.html"]
            if nav_hrefs != expected_hrefs:
                errors.append(f"{offer_id} {href}: context navigation hrefs {nav_hrefs}, expected {expected_hrefs}")
'''
new_anchor = '''        breadcrumb = extract_class_block(html, "nav", "service-breadcrumbs")
        context_nav = extract_class_block(html, "nav", "service-context-nav")
        if not breadcrumb:
            errors.append(f"{offer_id} {href}: breadcrumb block unreadable")
            expected_anchor = None
        else:
            breadcrumb_hrefs = re.findall(r'<a\\s+href="([^\"]+)"', breadcrumb, re.I)
            expected_anchor = breadcrumb_hrefs[-1] if breadcrumb_hrefs else None
            if not expected_anchor or not expected_anchor.endswith(f"#{offer_id.lower()}"):
                errors.append(f"{offer_id} {href}: breadcrumb family route does not end with #{offer_id.lower()}")
        if not context_nav:
            errors.append(f"{offer_id} {href}: context navigation block unreadable")
        elif expected_anchor:
            nav_hrefs = re.findall(r'<a\\s+href="([^\"]+)"', context_nav, re.I)
            expected_hrefs = [expected_anchor, "catalogue.html", "index.html"]
            if nav_hrefs != expected_hrefs:
                errors.append(f"{offer_id} {href}: context navigation hrefs {nav_hrefs}, expected {expected_hrefs}")
'''
t = replace_once(t, old_anchor, new_anchor, 'whole-estate family nav QA')
t = t.replace(
    'print("Verified common-contract pages plus separately accepted non-Operations reference-page source boundaries, one-H1, noindex, CSP, skip-link and contact-route requirements")',
    'print("Verified all 53 current DEVELOP pages against one common product-page contract, one-H1, noindex, CSP, skip-link and contact-route requirements")',
)
t = t.replace(
    'print("Verified HOC-015 through HOC-023 against one canonical Operations structure, module order, mandatory disclosures, global shell and optional-module controls")',
    'print("Verified all 53 current DEVELOP pages against one canonical structure, module order, mandatory disclosures, global shell and optional-module controls")',
)
write(p, t)

print('Applied 53-page canonical product-page alignment updates.')
