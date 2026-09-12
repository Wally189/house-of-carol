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

ALLOWED_PRICES = {
    "ai-data-use-rules-sprint.html": "£1,250",
    "ai-policy-and-sop-implementation-service.html": "£1,500",
    "responsible-ai-workplace-training.html": "£750",
    "role-based-ai-skills-workshop.html": "£1,250",
    "ai-workflow-opportunity-review.html": "£900",
    "ai-workflow-implementation-sprint.html": "£1,500",
    "independent-document-review.html": "£750",
    "process-design-sprint.html": "£1,500",
    "shared-drive-cleanup.html": "£1,250",
    "management-information-and-kpi-setup.html": "£1,250",
    "customer-journey-and-service-operations-review.html": "£1,250",
    "research-briefing.html": "£900",
    "church-and-parish-grant-funding-research.html": "£595",
    "website-completion-sprint.html": "£1,250",
}

REFERENCE_PAGES = {
    "ai-data-use-rules-sprint.html",
    "role-based-ai-skills-workshop.html",
    "ai-workflow-opportunity-review.html",
    "ai-workflow-implementation-sprint.html",
    "process-design-sprint.html",
    "customer-journey-and-service-operations-review.html",
    "website-completion-sprint.html",
}

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
        r'<article class="service-entry" id="hoc-\d+" data-offer-id="(HOC-\d{3})">\s*<a class="service-card-link" href="([^"]+)">',
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
        "native disclosure": '<details class="hoc-accordion">' in html and '<summary>' in html,
        "context navigation": 'class="service-context-nav"' in html,
    }
    for label, ok in checks.items():
        if not ok:
            errors.append(f"{offer_id} {href}: missing {label}")

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
    allowed = ALLOWED_PRICES.get(href)
    if allowed:
        if allowed not in pounds:
            errors.append(f"{offer_id} {href}: authoritative price {allowed} missing")
        unexpected = pounds - {allowed}
        if unexpected:
            errors.append(f"{offer_id} {href}: unexpected numeric price(s): {sorted(unexpected)}")
    elif pounds:
        errors.append(f"{offer_id} {href}: generic/unpriced page contains numeric price(s): {sorted(pounds)}")

    # Whole-estate completion contract. Existing best-in-class references retain
    # their proven bespoke information architecture; every rewritten page must
    # carry the full common customer-information contract.
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
print(f"Verified {len(ALLOWED_PRICES)} offer-specific numeric price boundaries and {len(routes) - len(ALLOWED_PRICES)} non-numeric pricing mechanisms")
print("Verified customer-information contract, substantive deliverable copy, native disclosure, one-H1, noindex, CSP, skip-link and contact-route requirements")
print("Verified all 11 TBD offers remain unexposed and BrandLab is not a product route")
