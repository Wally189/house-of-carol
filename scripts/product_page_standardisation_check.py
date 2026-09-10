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

EXPECTED_IDS = {f"HOC-{n:03d}" for n in range(1, 57)} - {
    "HOC-027", "HOC-036", "HOC-044", "HOC-054"
}
ALLOWED_PRICES = {
    "independent-document-review.html": "£750",
    "process-design-sprint.html": "£1,500",
    "shared-drive-cleanup.html": "£1,250",
    "research-briefing.html": "£900",
}
FORBIDDEN_CUSTOMER_STRINGS = (
    "DEVELOP FOR 02/10",
    "EXTERNAL PROOF REQUIRED",
    "Customer 000",
    "INTERNAL BUILD PASS",
    "PROPRIETOR-APPROVED",
)

errors = []
routes = {}

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

if len(routes) != 52:
    errors.append(f"Expected 52 current DEVELOP product routes; found {len(routes)}")

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
        "contact CTA": 'href="contact.html"' in html,
        "native disclosure": '<details class="hoc-accordion">' in html and '<summary>' in html,
    }
    for label, ok in checks.items():
        if not ok:
            errors.append(f"{offer_id} {href}: missing {label}")

    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        errors.append(f"{offer_id} {href}: must contain exactly one H1")
    if re.search(r"<script\b", html, re.I):
        errors.append(f"{offer_id} {href}: script element present despite no-script page model")
    if re.search(r"<details\b[^>]*>.*?<details\b", html, re.I | re.S):
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

# The three current TBD portfolio gaps must not be exposed as catalogue entries.
for tbd in ("HOC-036", "HOC-044", "HOC-054"):
    if tbd in routes:
        errors.append(f"TBD offer exposed as product route: {tbd}")

# BrandLab pages are experiments, not product routes.
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
print("Verified 4 offer-specific numeric price boundaries and 48 non-numeric pricing mechanisms")
print("Verified native disclosure, one-H1, noindex, CSP, skip-link and contact-route requirements")
print("Verified HOC-036/HOC-044/HOC-054 remain unexposed and BrandLab is not a product route")
