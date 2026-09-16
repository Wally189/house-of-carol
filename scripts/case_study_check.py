from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RETAINED = [
    'worked-example-process-handover.html',
    'worked-example-trade-account-customer-journey.html',
    'worked-example-ai-workflow.html',
]
INDEX = 'worked-examples.html'
FORBIDDEN = (
    'fictional worked example',
    'fictional organisation',
    'fictional b2b service business',
    'fictional trade-supply business',
    'if this were real work',
    'if this were a real review',
)
DISCLOSURE = 'Illustrative example — shown to explain how the service can be applied. It is not a customer testimonial or measured result.'


def fail(message):
    raise SystemExit('FAIL: ' + message)


index = ROOT / INDEX
if not index.exists():
    fail('worked-examples.html missing')
index_text = index.read_text(encoding='utf-8')
for page in RETAINED:
    if index_text.count(f'href="{page}"') != 1:
        fail(f'worked-example index must link exactly once to {page}')
if index_text.count('class="worked-example-card"') != 3:
    fail('worked-example index must contain exactly three retained cards')
if 'customer testimonial' not in index_text.lower() or 'measured result' not in index_text.lower():
    fail('worked-example index evidence boundary missing')

for page in RETAINED:
    path = ROOT / page
    if not path.exists():
        fail('missing ' + page)
    text = path.read_text(encoding='utf-8')
    low = text.lower()
    required = [
        'lang="en-GB"',
        'name="viewport"',
        'name="robots" content="noindex,nofollow"',
        "script-src 'none'",
        'class="skip" href="#main"',
        'id="main"',
        'WORKED EXAMPLE',
        DISCLOSURE,
        'Situation',
        'What House of Carol would look at',
        'What a clearer state could look like',
        'What the customer could receive',
        'What might logically follow',
    ]
    for marker in required:
        if marker.lower() not in low:
            fail(f'{page}: missing {marker}')
    for forbidden in FORBIDDEN:
        if forbidden in low:
            fail(f'{page}: superseded customer-facing wording remains: {forbidden}')
    if re.search(r'<script\b', text, re.I):
        fail(page + ': script present')
    if re.search(r'\sstyle\s*=', text, re.I):
        fail(page + ': inline style present')
    if len(re.findall(r'<h1\b', text, re.I)) != 1:
        fail(page + ': expected one H1')

if list(ROOT.glob('case-study-*.html')):
    fail('superseded generated case-study pages remain in build workspace')
if (ROOT / 'case-studies.html').exists():
    fail('superseded generated case-study index remains in build workspace')

print('PASS: exactly three retained worked-example pages and their index remain; evidence-honest terminology, customer logic, noindex/CSP and removal of the superseded 53-page generated case-study layer are verified')
