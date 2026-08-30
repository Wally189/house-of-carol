from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = 'run13-integrity-20260831a'


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)

# Review/test scaffolding must never be present in the public release tree.
for pattern in ('qa-run*.txt', 'README-RUN*.tmp', 'RUN*-REVIEW.md'):
    matches = sorted(p.name for p in ROOT.glob(pattern))
    if matches:
        fail(f'public release contains review scaffolding matching {pattern}: {matches}')

# The two material customer-facing surfaces must identify the exact release family
# and load a uniquely named integrity-recovery layer. This is observability, not
# proof that the visual outcome has been accepted on a real device.
for name in ('index.html', 'catalogue.html'):
    text = (ROOT / name).read_text(encoding='utf-8')
    marker = f'<meta name="hoc-build" content="{BUILD}">' 
    if marker not in text:
        fail(f'{name}: missing exact build marker {BUILD}')
    if 'assets/hoc-run13-touch.css' not in text:
        fail(f'{name}: Run 13 touch/release-identity layer not loaded')
    if 'noindex,nofollow' not in text:
        fail(f'{name}: noindex containment missing')

print('PASS: Run 13 public-tree scaffolding and release-identity checks')
