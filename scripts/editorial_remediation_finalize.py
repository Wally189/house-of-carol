from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

CHURCH_ROUTES = {
    'church-and-parish-grant-funding-research.html': (
        ('temporal project', 'practical project'),
        ('Temporal project', 'Practical project'),
        ('temporal service only', 'practical funding research only'),
        ('Temporal service only', 'Practical funding research only'),
    ),
    'church-grant-application-development-support.html': (
        ('prioritised temporal works-and-funding roadmap', 'prioritised works-and-funding roadmap'),
        ('Prioritised temporal works-and-funding roadmap', 'Prioritised works-and-funding roadmap'),
        ('temporal service only', 'practical application support only'),
        ('Temporal service only', 'Practical application support only'),
        ('temporal application support', 'practical application support'),
        ('Temporal application support', 'Practical application support'),
    ),
    'church-building-funding-and-maintenance-roadmap.html': (
        ('temporal needs', 'building needs'),
        ('Temporal needs', 'Building needs'),
        ('recurring temporal administration', 'recurring parish administration'),
        ('Recurring temporal administration', 'Recurring parish administration'),
        ('temporal works-and-funding', 'works-and-funding'),
        ('Temporal works-and-funding', 'Works-and-funding'),
        ('temporal works', 'building works'),
        ('Temporal works', 'Building works'),
        ('temporal programme', 'practical programme'),
        ('Temporal programme', 'Practical programme'),
        ('temporal service only', 'practical planning support only'),
        ('Temporal service only', 'Practical planning support only'),
    ),
    'parish-operations-and-administration-improvement.html': (
        ('temporal parish administration', 'parish administration'),
        ('Temporal parish administration', 'Parish administration'),
        ('temporal administration', 'parish administration'),
        ('Temporal administration', 'Parish administration'),
        ('temporal service only', 'practical administration support only'),
        ('Temporal service only', 'Practical administration support only'),
    ),
    'parish-digital-and-ai-governance-starter-service.html': (
        ('temporal service only', 'practical digital-governance support only'),
        ('Temporal service only', 'Practical digital-governance support only'),
    ),
    'parish-communications-service.html': (
        ('temporal communications', 'parish communications'),
        ('Temporal communications', 'Parish communications'),
        ('temporal service only', 'practical communications support only'),
        ('Temporal service only', 'Practical communications support only'),
    ),
}

for route, replacements in CHURCH_ROUTES.items():
    path = ROOT / route
    html = path.read_text(encoding='utf-8')
    for old, new in replacements:
        html = html.replace(old, new)
    remaining = list(re.finditer(r'\btemporal\b', html, re.I))
    if remaining:
        snippets = []
        for match in remaining[:5]:
            start = max(0, match.start() - 80)
            end = min(len(html), match.end() + 80)
            snippets.append(re.sub(r'\s+', ' ', html[start:end]))
        raise SystemExit(f"EDITORIAL REMEDIATION FAIL: {route} still contains customer-facing temporal language: {' | '.join(snippets)}")
    path.write_text(html, encoding='utf-8')

print('PASS: Church/parish customer wording uses plain operational language with authority boundaries preserved')
