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
ROUTE_RE = re.compile(r'<article class="service-entry(?: [^"]*)?" id="hoc-\d+" data-offer-id="(HOC-\d{3})">\s*<a class="service-card-link" href="([^"]+)">', re.I)
FORBIDDEN = {
    "case-study language": re.compile(r"\bcase[ -]?stud(?:y|ies)\b", re.I),
    "example language": re.compile(r"\bexamples?\b", re.I),
    "worked-example markup or link": re.compile(r"worked-example", re.I),
}
routes = {}
errors = []
for category in CATEGORY_PAGES:
    path = ROOT / category
    if not path.exists():
        errors.append(f"Missing category page: {category}")
        continue
    for offer_id, href in ROUTE_RE.findall(path.read_text(encoding="utf-8")):
        routes[offer_id] = href
if len(routes) != 53:
    errors.append(f"Expected 53 current product routes; found {len(routes)}")
for offer_id, href in sorted(routes.items()):
    path = ROOT / href
    if not path.exists():
        errors.append(f"{offer_id}: missing product page {href}")
        continue
    html = path.read_text(encoding="utf-8")
    for label, pattern in FORBIDDEN.items():
        for match in pattern.finditer(html):
            start = max(0, match.start() - 120)
            end = min(len(html), match.end() + 120)
            context = re.sub(r"\s+", " ", html[start:end]).strip()
            errors.append(f"{offer_id} {href}: forbidden {label}: {match.group(0)!r} :: {context}")
if errors:
    print("FAIL: product pages must contain no case studies or examples.")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)
print(f"PASS: {len(routes)} product pages contain no case studies or examples.")
