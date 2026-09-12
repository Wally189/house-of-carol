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

# Pages with an authoritative bespoke customer-information architecture are
# checked against their own source boundary rather than forced into the common
# rewritten-page contract.
REFERENCE_PAGES = {
    "ai-data-use-rules-sprint.html",
    "role-based-ai-skills-workshop.html",
    "ai-workflow-opportunity-review.html",
    "ai-workflow-implementation-sprint.html",
    "process-design-sprint.html",
    "shared-drive-cleanup.html",
    "management-information-and-kpi-setup.html",
    "customer-journey-and-service-operations-review.html",
    "website-completion-sprint.html",
}

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
    "What House of Carol does not promise",
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
    allowed = ALLOWED_PRICES.get(href)
    if allowed:
        if allowed not in pounds:
            errors.append(f"{offer_id} {href}: authoritative price {allowed} missing")
        unexpected = pounds - {allowed}
        if unexpected:
            errors.append(f"{offer_id} {href}: unexpected numeric price(s): {sorted(unexpected)}")
    elif pounds:
        errors.append(f"{offer_id} {href}: generic/unpriced page contains numeric price(s): {sorted(pounds)}")

    # Whole-estate completion contract. Existing best-in-class or separately
    # accepted reference pages retain their proven bespoke information
    # architecture; rewritten pages carry the full common contract.
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

    if href == "shared-drive-cleanup.html":
        for marker in HOC016_REQUIRED_MARKERS:
            if marker not in html:
                errors.append(f"{offer_id} {href}: accepted Candidate 01 marker missing: {marker}")
        for drift in HOC016_FORBIDDEN_DRIFT:
            if drift.lower() in html.lower():
                errors.append(f"{offer_id} {href}: superseded HOC-016 wording remains: {drift}")
        if '<details' in html.lower():
            errors.append(f"{offer_id} {href}: accepted Candidate 01 should not be redesigned into disclosure accordions")

    if href == "management-information-and-kpi-setup.html":
        for marker in HOC017_REQUIRED_MARKERS:
            if marker not in html:
                errors.append(f"{offer_id} {href}: approved HOC-017 marker missing: {marker}")
        for drift in HOC017_FORBIDDEN_DRIFT:
            if drift.lower() in html.lower():
                errors.append(f"{offer_id} {href}: superseded HOC-017 wording remains: {drift}")

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
print("Verified common-contract pages plus authoritative bespoke reference-page source boundaries, one-H1, noindex, CSP, skip-link and contact-route requirements")
print("Verified HOC-016 against accepted Candidate 01 markers without forcing a redesign")
print("Verified HOC-017 against approved customer-facing markers and superseded-copy drift checks")
print("Verified all 11 TBD offers remain unexposed and BrandLab is not a product route")
