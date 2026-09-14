from pathlib import Path

p = Path(__file__).resolve().parent / 'product_page_standardisation_check.py'
t = p.read_text(encoding='utf-8')
old = '''def normalise_markup(fragment: str) -> str:
    return re.sub(r'\\s+', ' ', fragment).strip()

def extract_class_block'''
new = '''def normalise_markup(fragment: str) -> str:
    fragment = re.sub(r'\\s+', ' ', fragment).strip()
    return re.sub(r'>\\s+<', '><', fragment)

def extract_class_block'''
if old not in t:
    raise SystemExit('normalise_markup target not found')
t = t.replace(old, new, 1)
old = '''def stylesheet_hrefs(markup: str):
    return re.findall(r'<link\\s+rel="stylesheet"\\s+href="([^\"]+)"', markup, re.I)
'''
new = '''def stylesheet_hrefs(markup: str):
    hrefs = re.findall(r'<link\\s+rel="stylesheet"\\s+href="([^\"]+)"', markup, re.I)
    return [href.split("?", 1)[0] for href in hrefs]
'''
if old not in t:
    raise SystemExit('stylesheet_hrefs target not found')
t = t.replace(old, new, 1)
old = '''            "hero scope": html.count('class="product-scope-line"'),
'''
if old not in t:
    raise SystemExit('hero-scope cardinality target not found')
t = t.replace(old, '', 1)
p.write_text(t, encoding='utf-8')
print('Corrected whole-estate structural QA normalisation rules.')
