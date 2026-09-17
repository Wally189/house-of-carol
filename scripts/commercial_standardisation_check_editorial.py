from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scripts' / 'commercial_standardisation_check.py'
text = source.read_text(encoding='utf-8')

# Change only literal customer-facing headings superseded by the approved
# 17 September 2026 editorial remediation. All commercial journey, module
# order, adjacency, current-route, non-self, identity, internal-language and
# local-link assertions continue to execute unchanged.
text = text.replace('SEE HOW THIS CAN WORK', 'See how this can work')
text = text.replace('WHERE THIS COULD LEAD NEXT', 'Where this could lead next')
text = text.replace('A defined engagement', 'What the engagement looks like')

code = compile(text, str(source), 'exec')
exec(code, {'__name__': '__main__', '__file__': str(source)})
