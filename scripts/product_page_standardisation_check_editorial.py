from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scripts' / 'product_page_standardisation_check.py'
text = source.read_text(encoding='utf-8')

# Change only the literal customer-facing wording expectations superseded by
# the approved 17 September 2026 editorial remediation. All existing route,
# price, structure, cardinality, CSP, navigation and drift assertions execute.
text = text.replace(
    '"<summary>What does House of Carol not promise?</summary>"',
    '"<summary>What this service does not promise</summary>"',
)
text = text.replace(
    '"<h2>A defined engagement</h2>"',
    '"<h2>What the engagement looks like</h2>"',
)
text = text.replace(
    'HOC017_REQUIRED_MARKERS = (\n    "Management Reporting Setup",',
    'HOC017_REQUIRED_MARKERS = (\n    "Management Information &amp; KPI Setup",',
)
text = text.replace(
    'HOC017_FORBIDDEN_DRIFT = (\n    "Management Information &amp; KPI Setup",',
    'HOC017_FORBIDDEN_DRIFT = (\n    "Management Reporting Setup",',
)

code = compile(text, str(source), 'exec')
exec(code, {'__name__': '__main__', '__file__': str(source)})
