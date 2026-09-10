from pathlib import Path
import html as html_lib
import re

ROOT = Path(__file__).resolve().parents[1]
AREA_PAGES = [
    "catalogue-ai-digital.html",
    "catalogue-operations.html",
    "catalogue-commercial.html",
    "catalogue-learning.html",
    "catalogue-research.html",
    "catalogue-charity-public.html",
    "catalogue-church-parish.html",
]

routes = []
for area in AREA_PAGES:
    text = (ROOT / area).read_text(encoding="utf-8")
    routes.extend(re.findall(r'<a class="service-card-link" href="([^"]+\.html)">', text))

changed = []
for route in sorted(set(routes)):
    path = ROOT / route
    text = path.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>', text, re.I):
        continue
    hook = re.search(r'<p class="product-hook"><strong>(.*?)</strong></p>', text, re.I | re.S)
    if not hook:
        raise SystemExit(f"No product hook available for missing description: {route}")
    description = re.sub(r'<[^>]+>', '', hook.group(1))
    description = html_lib.unescape(description)
    description = ' '.join(description.split())
    description = html_lib.escape(description, quote=True)
    title_end = re.search(r'</title>', text, re.I)
    if not title_end:
        raise SystemExit(f"No title element: {route}")
    insertion = f'<meta name="description" content="{description}">'
    text = text[:title_end.end()] + insertion + text[title_end.end():]
    path.write_text(text, encoding="utf-8")
    changed.append(route)

print(f"Added descriptions to {len(changed)} product pages")
for route in changed:
    print(route)
