from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_PAGES = [
    "catalogue-ai-digital.html",
    "catalogue-operations.html",
    "catalogue-commercial.html",
    "catalogue-learning.html",
    "catalogue-church-parish.html",
    "catalogue-charity-public.html",
    "catalogue-research.html",
]

TBD_IDS = {
    "HOC-027", "HOC-036", "HOC-044", "HOC-054", "HOC-057",
    "HOC-058", "HOC-059", "HOC-060", "HOC-061", "HOC-062", "HOC-063",
}
EXPECTED_IDS = {f"HOC-{n:03d}" for n in range(1, 65)} - TBD_IDS

# Owner-approved website pricing settlement, 12 September 2026.
# Each DEVELOP route must expose exactly this set of GBP amounts. Sets are
# used because a price can legitimately appear more than once on one page
# (for example in the hero and the service-facts block).
EXPECTED_PRICES = {
    "ai-data-use-rules-sprint.html": {"£1,250"},
    "ai-policy-and-sop-implementation-service.html": {"£1,500"},
    "responsible-ai-workplace-training.html": {"£750"},
    "role-based-ai-skills-workshop.html": {"£1,250"},
    "ai-leadership-and-management-workshop.html": {"£700", "£950", "£1,250"},
    "ai-workflow-opportunity-review.html": {"£900"},
    "ai-workflow-implementation-sprint.html": {"£1,500"},
    "ai-tool-and-account-governance-review.html": {"£750", "£1,250", "£2,000"},
    "ai-vendor-tool-selection-review.html": {"£850", "£1,250", "£1,750"},
    "independent-document-review.html": {"£750"},
    "ai-operating-model-and-governance-blueprint.html": {"£1,250", "£1,750", "£2,500"},
    "ai-adoption-support-retainer.html": {"£300", "£900"},
    "no-code-ai-automation-implementation.html": {"£1,500", "£3,500"},
    "business-knowledge-base-and-ai-retrieval-setup.html": {"£1,000", "£1,500", "£2,250"},
    "process-design-sprint.html": {"£1,500"},
    "shared-drive-cleanup.html": {"£1,250"},
    "management-information-and-kpi-setup.html": {"£1,250"},
    "customer-journey-and-service-operations-review.html": {"£1,250"},
    "customer-support-knowledge-base-build.html": {"£1,250", "£1,750", "£2,500"},
    "business-continuity-and-operational-readiness-pack.html": {"£1,250", "£1,750", "£2,500"},
    "decision-rights-and-governance-review.html": {"£950", "£1,250", "£1,750"},
    "complaints-and-redress-process-design.html": {"£1,000", "£1,500", "£2,250"},
    "evidence-and-marketing-claim-substantiation-review.html": {"£750", "£1,000", "£1,500"},
    "tender-review.html": {"£750", "£850", "£950"},
    "tender-readiness-and-bid-evidence-library.html": {"£1,250", "£1,750", "£2,500"},
    "public-procurement-opportunity-monitoring.html": {"£250", "£600"},
    "invoice-to-cash-process-setup.html": {"£1,000", "£1,500", "£2,250"},
    "cash-flow-and-financial-operations-setup.html": {"£1,000", "£1,500", "£2,250"},
    "supplier-and-purchasing-process-setup.html": {"£1,000", "£1,500", "£2,250"},
    "bespoke-organisational-training-design.html": {"£1,250", "£1,750", "£2,500"},
    "assessment-and-competency-framework-design.html": {"£1,250", "£1,750", "£2,500"},
    "internal-academy-learning-pathway-design.html": {"£1,500", "£2,000", "£3,000"},
    "microlearning-and-scenario-assessment-packs.html": {"£750", "£1,250", "£1,750"},
    "research-briefing.html": {"£900"},
    "training-quality-review.html": {"£750", "£1,250", "£1,750"},
    "church-and-parish-grant-funding-research.html": {"£595"},
    "church-grant-application-development-support.html": {"£1,250", "£1,750", "£2,500"},
    "church-building-funding-and-maintenance-roadmap.html": {"£1,250", "£1,750", "£2,500"},
    "parish-operations-and-administration-improvement.html": {"£1,250", "£1,750", "£2,500"},
    "parish-digital-and-ai-governance-starter-service.html": {"£1,000", "£1,500", "£2,250"},
    "parish-communications-service.html": {"£350", "£650"},
    "charity-ai-governance-pack-and-implementation.html": {"£1,250", "£1,750", "£2,500"},
    "charity-cyber-and-digital-governance-readiness-review.html": {"£750", "£1,250", "£1,750"},
    "charity-governance-and-trustee-information-pack-review.html": {"£750", "£1,250", "£1,750"},
    "public-sector-decision-governance-review.html": {"£1,250", "£2,500"},
    "committee-board-paper-quality-review.html": {"£750", "£1,000", "£1,500"},
    "public-sector-sop-and-process-modernisation.html": {"£1,250", "£1,750", "£2,500"},
    "consultation-and-evidence-synthesis-service.html": {"£1,250", "£1,750", "£2,500"},
    "evidence-based-executive-briefing-service.html": {"£750", "£1,500"},
    "b2b-charity-newsletter-production.html": {"£350", "£650", "£850"},
    "explainer-and-thought-leadership-production.html": {"£750", "£2,000"},
    "research-monitoring-horizon-scanning-subscription.html": {"£500", "£1,500"},
    "website-completion-sprint.html": {"£1,250"},
}

# All 53 current DEVELOP product pages use one canonical structural contract.
REFERENCE_PAGES = set()

CANONICAL_PAGES = set(EXPECTED_PRICES)

MANDATORY_OPERATION_DISCLOSURES = (
    "<summary>What needs to be in place?</summary>",
    "<summary>What is outside the scope?</summary>",
    "<summary>Is this the right service?</summary>",
    "<summary>What does House of Carol not promise?</summary>",
)

HOC016_REQUIRED_MARKERS = (
    "Shared drives rarely become a mess all at once.",
    "Nobody wants to delete anything because nobody is certain what is still needed.",
    "House of Carol takes one shared document area, works out what is actually going on, and gives you a simpler structure and a controlled plan for putting it right.",
    "A keep / move / archive / review plan.",
    "Nothing is deleted or moved by House of Carol under the standard review without explicit customer approval.",
    "Normally returned within 7 working days once the agreed access/inventory and discovery inputs are complete.",
    "Safe read-only access where appropriate, or a sufficient folder/file inventory, screenshots or directory listing.",
    "If everyone can reliably find the current version, ownership is clear and the problem is mostly that you dislike the folder names, keep your £1,250.",
    "No attempt to turn one messy team drive into an enterprise information-governance programme.",
    "Where does your team lose track of the right document?",
    "Discuss the shared drive",
)

HOC016_FORBIDDEN_DRIFT = (
    "Shared document areas rarely become a mess all at once.",
    "House of Carol reviews one shared document area",
    "The current standard engagement is for organisation-paid work",
)

HOC017_REQUIRED_MARKERS = (
    "Management Reporting Setup",
    "Make the numbers you already have useful for management decisions.",
    "£1,250 fixed",
    "5–8 management measures",
    "five existing systems or files",
    "one correction round for errors in the agreed work.",
    "This is a <strong>management-information service</strong>, not an accounting or financial-advice service.",
    "Check whether this service fits",
)

HOC017_FORBIDDEN_DRIFT = (
    "Management Information &amp; KPI Setup",
    "standard scope",
    "bounded correction cycle",
    "platform-neutral specification",
    "decision-linked KPIs",
)

FORBIDDEN_CUSTOMER_STRINGS = (
    "DEVELOP FOR 02/10",
    "EXTERNAL PROOF REQUIRED",
    "Customer 000",
    "INTERNAL BUILD PASS",
    "PROPRIETOR-APPROVED",
    "R0 INTERNAL ONLY",
    "A2 PARTIAL",
    "A2 COMPLETE",
    "BUYER-TEST",
    "PROPRIETOR DECISION",
    "LIVE-PAID",
    "PRE-BUYER",
)

errors = []
routes = {}
canonical_snapshots = {}

def has_nested_details(markup: str) -> bool:
    depth = 0
    for match in re.finditer(r'</?details\b[^>]*>', markup, re.I):
        token = match.group(0)
        if token.startswith('</'):
            depth = max(0, depth - 1)
        else:
            if depth > 0:
                return True
            depth += 1
    return False

def plain(fragment: str) -> str:
    fragment = re.sub(r'<[^>]+>', ' ', fragment)
    fragment = re.sub(r'\s+', ' ', fragment).strip().casefold()
    return fragment.strip(' .:;–—-')

def normalise_markup(fragment: str) -> str:
    fragment = re.sub(r'\s+', ' ', fragment).strip()
    return re.sub(r'>\s+<', '><', fragment)

def extract_class_block(markup: str, tag: str, class_name: str):
    match = re.search(
        rf'<{tag}\b[^>]*class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>.*?</{tag}>',
        markup,
        re.I | re.S,
    )
    return normalise_markup(match.group(0)) if match else None

def stylesheet_hrefs(markup: str):
    hrefs = re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+)"', markup, re.I)
    return [href.split("?", 1)[0] for href in hrefs]

def csp_value(markup: str):
    match = re.search(
        r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"',
        markup,
        re.I,
    )
    return normalise_markup(match.group(1)) if match else None

def placeholder_deliverables(markup: str):
    """Reject generated cards where the body merely repeats the heading."""
    block = re.search(
        r'<div class="deliverable-groups generic-deliverables">(.*?)</div>',
        markup,
        re.I | re.S,
    )
    if not block:
        return []
    defects = []
    for heading, body in re.findall(
        r'<article>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*</article>',
        block.group(1),
        re.I | re.S,
    ):
        h = plain(heading)
        b = plain(body)
        if h and b and h == b:
            defects.append(h)
    return defects

for category in CATEGORY_PAGES:
    path = ROOT / category
    if not path.exists():
        errors.append(f"Missing category page: {category}")
        continue
    html = path.read_text(encoding="utf-8")
    for match in re.finditer(
        r'<article class="service-entry(?: [^"]*)?" id="hoc-\d+" data-offer-id="(HOC-\d{3})">\s*<a class="service-card-link" href="([^"]+)">',
        html,
        re.I,
    ):
        offer_id, href = match.groups()
        if offer_id in routes:
            errors.append(f"Duplicate catalogue offer id: {offer_id}")
        routes[offer_id] = href

if set(routes) != EXPECTED_IDS:
    missing = sorted(EXPECTED_IDS - set(routes))
    extra = sorted(set(routes) - EXPECTED_IDS)
    if missing:
        errors.append("Missing DEVELOP routes: " + ", ".join(missing))
    if extra:
        errors.append("Unexpected/TBD routes exposed: " + ", ".join(extra))

if len(routes) != 53:
    errors.append(f"Expected 53 current DEVELOP product routes; found {len(routes)}")

route_hrefs = set(routes.values())
price_hrefs = set(EXPECTED_PRICES)
if len(EXPECTED_PRICES) != 53:
    errors.append(f"Expected 53 approved pricing entries; found {len(EXPECTED_PRICES)}")
if route_hrefs != price_hrefs:
    missing_prices = sorted(route_hrefs - price_hrefs)
    extra_prices = sorted(price_hrefs - route_hrefs)
    if missing_prices:
        errors.append("DEVELOP routes without approved pricing contract: " + ", ".join(missing_prices))
    if extra_prices:
        errors.append("Approved pricing entries without DEVELOP route: " + ", ".join(extra_prices))

seen_hrefs = set()
for offer_id, href in sorted(routes.items()):
    if href in seen_hrefs:
        errors.append(f"Duplicate product href: {href}")
    seen_hrefs.add(href)
    path = ROOT / href
    if not path.exists():
        errors.append(f"{offer_id}: route file missing: {href}")
        continue
    html = path.read_text(encoding="utf-8")

    checks = {
        "lang en-GB": 'lang="en-GB"' in html,
        "viewport": 'name="viewport"' in html,
        "noindex,nofollow": 'name="robots" content="noindex,nofollow"' in html,
        "CSP script-src none": "script-src 'none'" in html,
        "skip link": 'class="skip" href="#main"' in html,
        "main target": 'id="main"' in html,
        "product hero": 'class="product-hero' in html,
        "breadcrumb": 'aria-label="Breadcrumb"' in html,
        "contact CTA": 'href="contact.html"' in html or 'href="index.html#contact"' in html,
        "context navigation": 'class="service-context-nav"' in html,
    }
    for label, ok in checks.items():
        if not ok:
            errors.append(f"{offer_id} {href}: missing {label}")

    if href not in REFERENCE_PAGES:
        if '<details class="hoc-accordion">' not in html or '<summary>' not in html:
            errors.append(f"{offer_id} {href}: missing native disclosure")

    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        errors.append(f"{offer_id} {href}: must contain exactly one H1")
    if re.search(r"<script\b", html, re.I):
        errors.append(f"{offer_id} {href}: script element present despite no-script page model")
    if has_nested_details(html):
        errors.append(f"{offer_id} {href}: nested details/accordion found")
    for forbidden in FORBIDDEN_CUSTOMER_STRINGS:
        if forbidden.lower() in html.lower():
            errors.append(f"{offer_id} {href}: internal lifecycle language exposed: {forbidden}")

    pounds = set(re.findall(r"£[0-9][0-9,]*(?:\.[0-9]{1,2})?", html))
    expected_prices = EXPECTED_PRICES.get(href)
    if expected_prices is None:
        errors.append(f"{offer_id} {href}: no approved pricing contract")
    else:
        missing_prices = expected_prices - pounds
        unexpected_prices = pounds - expected_prices
        if missing_prices:
            errors.append(f"{offer_id} {href}: approved numeric price(s) missing: {sorted(missing_prices)}")
        if unexpected_prices:
            errors.append(f"{offer_id} {href}: unexpected numeric price(s): {sorted(unexpected_prices)}")
        if not pounds:
            errors.append(f"{offer_id} {href}: DEVELOP route has no numerical GBP pricing presentation")

    # Whole-estate completion contract. Separately accepted non-Operations
    # reference pages retain their proven source-bound information architecture;
    # every other page carries the common customer-information contract.
    if href not in REFERENCE_PAGES:
        contract = {
            "outcome hook": 'class="product-hook"' in html,
            "audience": 'class="product-audience"' in html,
            "pricing fact": "<dt>Pricing</dt>" in html,
            "scope fact": "<dt>Scope</dt>" in html,
            "what changes": "<h2>What changes</h2>" in html,
            "deliverables": "<h2>What you will receive</h2>" in html,
            "requirements disclosure": "<summary>What needs to be in place?</summary>" in html,
            "exclusions disclosure": "<summary>What is outside the scope?</summary>" in html,
            "fit disclosure": "<summary>Is this the right service?</summary>" in html,
            "claim boundary": "<summary>What does House of Carol not promise?</summary>" in html,
        }
        for label, ok in contract.items():
            if not ok:
                errors.append(f"{offer_id} {href}: page-contract failure: {label}")

        repeated = placeholder_deliverables(html)
        if repeated:
            errors.append(
                f"{offer_id} {href}: placeholder deliverable description repeats heading: "
                + ", ".join(repeated)
            )

    if href in CANONICAL_PAGES:
        operations_contract = {
            "standard hero": 'class="product-hero standard-product-hero"' in html,
            "outcome hook": 'class="product-hook"' in html,
            "audience": 'class="product-audience"' in html,
            "hero pricing": 'class="product-price product-fee-text"' in html,
            "hero scope": 'class="product-scope-line"' in html,
            "trust boundary": 'class="product-trust-line"' in html,
            "hero CTA": 'class="actions"' in html,
            "what changes": "<h2>What changes</h2>" in html,
            "deliverables": "<h2>What you will receive</h2>" in html,
            "generic deliverables": 'class="deliverable-groups generic-deliverables"' in html,
            "defined engagement": "<h2>A defined engagement</h2>" in html,
            "service facts": 'class="service-facts standard-service-facts"' in html,
            "service type fact": "<dt>Service type</dt>" in html,
            "delivery fact": "<dt>Delivery</dt>" in html,
            "pricing fact": "<dt>Pricing</dt>" in html,
            "scope fact": "<dt>Scope</dt>" in html,
            "disclosure group": 'class="hoc-accordion-group"' in html,
            "final CTA": 'class="shell cta-panel"' in html,
        }
        for label, ok in operations_contract.items():
            if not ok:
                errors.append(f"{offer_id} {href}: canonical-contract failure: {label}")

        cardinality = {
            "standard hero": html.count('class="product-hero standard-product-hero"'),
            "hero pricing": html.count('class="product-price product-fee-text"'),
            "trust boundary": html.count('class="product-trust-line"'),
            "hero CTA": html.count('class="actions"'),
            "What changes": html.count("<h2>What changes</h2>"),
            "What you will receive": html.count("<h2>What you will receive</h2>"),
            "defined engagement": html.count("<h2>A defined engagement</h2>"),
            "disclosure group": html.count('class="hoc-accordion-group"'),
            "final CTA": html.count('class="shell cta-panel"'),
            "context navigation": html.count('class="service-context-nav"'),
        }
        for label, count in cardinality.items():
            if count != 1:
                errors.append(f"{offer_id} {href}: canonical cardinality {label}={count}, expected 1")

        for disclosure in MANDATORY_OPERATION_DISCLOSURES:
            count = html.count(disclosure)
            if count != 1:
                errors.append(f"{offer_id} {href}: mandatory disclosure count {plain(disclosure)}={count}, expected 1")

        order_markers = (
            ("breadcrumbs", 'class="service-breadcrumbs"'),
            ("hero", 'class="product-hero standard-product-hero"'),
            ("what changes", "<h2>What changes</h2>"),
            ("deliverables", "<h2>What you will receive</h2>"),
            ("defined engagement", "<h2>A defined engagement</h2>"),
            ("disclosures", 'class="hoc-accordion-group"'),
            ("final CTA", 'class="shell cta-panel"'),
            ("context navigation", 'class="service-context-nav"'),
            ("footer", '<footer class="site-footer">'),
        )
        positions = [(label, html.find(marker)) for label, marker in order_markers]
        if any(position < 0 for _, position in positions):
            errors.append(f"{offer_id} {href}: canonical module-order marker missing")
        else:
            numeric_positions = [position for _, position in positions]
            if numeric_positions != sorted(numeric_positions) or len(set(numeric_positions)) != len(numeric_positions):
                errors.append(
                    f"{offer_id} {href}: canonical module order invalid: "
                    + " -> ".join(label for label, _ in positions)
                )

        breadcrumb = extract_class_block(html, "nav", "service-breadcrumbs")
        context_nav = extract_class_block(html, "nav", "service-context-nav")
        if not breadcrumb:
            errors.append(f"{offer_id} {href}: breadcrumb block unreadable")
            expected_anchor = None
        else:
            breadcrumb_hrefs = re.findall(r'<a\s+href="([^"]+)"', breadcrumb, re.I)
            expected_anchor = breadcrumb_hrefs[-1] if breadcrumb_hrefs else None
            if not expected_anchor or not expected_anchor.endswith(f"#{offer_id.lower()}"):
                errors.append(f"{offer_id} {href}: breadcrumb family route does not end with #{offer_id.lower()}")
        if not context_nav:
            errors.append(f"{offer_id} {href}: context navigation block unreadable")
        elif expected_anchor:
            nav_hrefs = re.findall(r'<a\s+href="([^"]+)"', context_nav, re.I)
            expected_hrefs = [expected_anchor, "catalogue.html", "index.html"]
            if nav_hrefs != expected_hrefs:
                errors.append(f"{offer_id} {href}: context navigation hrefs {nav_hrefs}, expected {expected_hrefs}")

        if 'class="worked-example-promo"' in html:
            worked = html.find('class="worked-example-promo"')
            deliverables = html.find("<h2>What you will receive</h2>")
            defined = html.find("<h2>A defined engagement</h2>")
            if not (deliverables < worked < defined):
                errors.append(f"{offer_id} {href}: worked example is outside its canonical slot")
            if 'class="worked-example-disclosure"' not in html:
                errors.append(f"{offer_id} {href}: worked example missing disclosure")

        if 'class="product-visual' in html:
            if "hoc015-preview.css" in html:
                errors.append(f"{offer_id} {href}: product visuals still depend on page-specific hoc015-preview.css")
            figures = re.findall(
                r'<figure\s+class="[^"]*product-visual[^"]*"[^>]*>(.*?)</figure>',
                html,
                re.I | re.S,
            )
            if not figures:
                errors.append(f"{offer_id} {href}: product visual marker exists without a figure")
            for index, figure in enumerate(figures, 1):
                image = re.search(r'<img\b([^>]*)>', figure, re.I | re.S)
                if not image:
                    errors.append(f"{offer_id} {href}: product visual {index} has no img")
                    continue
                attrs = image.group(1)
                alt = re.search(r'alt="([^"]*)"', attrs, re.I)
                if not alt or not alt.group(1).strip():
                    errors.append(f"{offer_id} {href}: product visual {index} missing meaningful alt text")
                if not re.search(r'\bwidth="\d+"', attrs, re.I) or not re.search(r'\bheight="\d+"', attrs, re.I):
                    errors.append(f"{offer_id} {href}: product visual {index} missing width/height")

        canonical_snapshots[href] = {
            "header": extract_class_block(html, "header", "site-header"),
            "footer": extract_class_block(html, "footer", "site-footer"),
            "stylesheets": stylesheet_hrefs(html),
            "csp": csp_value(html),
        }

    if href == "shared-drive-cleanup.html":
        for marker in HOC016_REQUIRED_MARKERS:
            if marker not in html:
                errors.append(f"{offer_id} {href}: accepted Candidate 01 marker missing: {marker}")
        for drift in HOC016_FORBIDDEN_DRIFT:
            if drift.lower() in html.lower():
                errors.append(f"{offer_id} {href}: superseded HOC-016 wording remains: {drift}")

    if href == "management-information-and-kpi-setup.html":
        for marker in HOC017_REQUIRED_MARKERS:
            if marker not in html:
                errors.append(f"{offer_id} {href}: approved HOC-017 marker missing: {marker}")
        for drift in HOC017_FORBIDDEN_DRIFT:
            if drift.lower() in html.lower():
                errors.append(f"{offer_id} {href}: superseded HOC-017 wording remains: {drift}")

if set(canonical_snapshots) != CANONICAL_PAGES:
    missing = sorted(CANONICAL_PAGES - set(canonical_snapshots))
    if missing:
        errors.append("Canonical snapshots missing: " + ", ".join(missing))
else:
    reference_href = "process-design-sprint.html"
    reference = canonical_snapshots[reference_href]
    if not reference["header"] or not reference["footer"] or not reference["csp"]:
        errors.append("Canonical reference page has unreadable global shell")
    for href in sorted(CANONICAL_PAGES):
        snapshot = canonical_snapshots[href]
        if snapshot["header"] != reference["header"]:
            errors.append(f"{href}: global header differs from canonical reference")
        if snapshot["footer"] != reference["footer"]:
            errors.append(f"{href}: global footer differs from canonical reference")
        if snapshot["stylesheets"] != reference["stylesheets"]:
            errors.append(
                f"{href}: stylesheet list differs from canonical reference: "
                f"{snapshot['stylesheets']} != {reference['stylesheets']}"
            )
        if snapshot["csp"] != reference["csp"]:
            errors.append(f"{href}: CSP differs from canonical reference")

for tbd in sorted(TBD_IDS):
    if tbd in routes:
        errors.append(f"TBD offer exposed as product route: {tbd}")

brandlab = {p.name for p in ROOT.glob("brandlab-*.html")}
if seen_hrefs & brandlab:
    errors.append("BrandLab experiment page exposed as a product route")

if errors:
    print("PRODUCT PAGE STANDARDISATION QA: FAIL", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("PRODUCT PAGE STANDARDISATION QA: PASS")
print(f"Verified {len(routes)} current DEVELOP product routes")
print(f"Verified {len(EXPECTED_PRICES)}/53 DEVELOP routes against their exact approved numerical GBP price sets")
print("Verified all 53 current DEVELOP pages against one common product-page contract, one-H1, noindex, CSP, skip-link and contact-route requirements")
print("Verified all 53 current DEVELOP pages against one canonical structure, module order, mandatory disclosures, global shell and optional-module controls")
print("Verified HOC-016 accepted Candidate 01 content markers while permitting canonical structural normalisation")
print("Verified HOC-017 approved customer-facing markers and superseded-copy drift checks")
print("Verified all 11 TBD offers remain unexposed and BrandLab is not a product route")
