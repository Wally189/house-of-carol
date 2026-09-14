from pathlib import Path
from bs4 import BeautifulSoup, Tag
import ast

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts' / 'product_page_standardisation_check.py'
script = CHECK.read_text(encoding='utf-8')
tree = ast.parse(script)
routes = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'EXPECTED_PRICES':
                routes = list(ast.literal_eval(node.value).keys())
if len(routes) != 53:
    raise SystemExit(f'Expected 53 product routes, found {len(routes)}')

allowed_css = {'hoc-rebuild.css','hoc-service.css','hoc-contact.css','hoc-catalogue.css'}

def heading(section):
    h = section.find('h2') if section else None
    return ' '.join(h.stripped_strings) if h else ''

for path in routes:
    p = ROOT / path
    soup = BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser')
    body = soup.body
    main = soup.find('main', id='main')
    if not body or not main:
        raise SystemExit(f'{path}: missing body/main')
    classes = list(body.get('class', []))
    if 'canonical-product-page' not in classes:
        classes.append('canonical-product-page')
    body['class'] = classes

    for link in list(soup.find_all('link', rel=lambda v: v and 'stylesheet' in v)):
        href = link.get('href','')
        name = href.split('?')[0].split('/')[-1]
        if name.startswith('hoc') and name not in allowed_css:
            link.decompose()
        elif name == 'hoc-service.css':
            link['href'] = 'assets/hoc-service.css?v=20260914-canonical-render-lock'

    breadcrumb = main.find('nav', class_='service-breadcrumbs', recursive=False)
    hero = main.find('section', class_=lambda c: c and 'product-hero' in c.split(), recursive=False)
    context = main.find('nav', class_='service-context-nav', recursive=False)
    sections = main.find_all('section', recursive=False)
    what = next((s for s in sections if heading(s) == 'What changes'), None)
    deliver = next((s for s in sections if heading(s) == 'What you will receive'), None)
    defined = next((s for s in sections if heading(s) == 'A defined engagement'), None)
    disclosures = next((s for s in sections if 'disclosures-section' in s.get('class', []) or s.find('summary', string=lambda x: x and 'What needs to be in place?' in x)), None)
    cta = next((s for s in sections if s.select_one('.cta-panel')), None)
    required = {'breadcrumb':breadcrumb,'hero':hero,'what':what,'deliver':deliver,'defined':defined,'disclosures':disclosures,'cta':cta,'context':context}
    missing = [k for k,v in required.items() if v is None]
    if missing:
        raise SystemExit(f'{path}: missing canonical modules {missing}')

    hero['class'] = ['product-hero','standard-product-hero']
    what['class'] = ['product-section','alt']
    deliver['class'] = ['product-section']
    defined['class'] = ['product-section','alt']
    disclosures['class'] = ['product-section','disclosures-section']
    cta['class'] = ['product-section','alt']

    dg = deliver.select_one('.deliverable-groups')
    if dg:
        dg['class'] = ['deliverable-groups','generic-deliverables']
    facts = defined.select_one('.service-facts')
    if facts:
        facts['class'] = ['service-facts','standard-service-facts']
    ag = disclosures.select_one('.hoc-accordion-group')
    if ag:
        ag['class'] = ['hoc-accordion-group']

    shell = hero.find('div', class_='shell', recursive=False)
    if shell:
        elems = [x for x in shell.contents if isinstance(x, Tag)]
        def rank(x):
            cls = x.get('class', [])
            if x.name == 'h1': return 10
            if 'product-hook' in cls: return 20
            if 'intro' in cls: return 30
            if 'product-platforms' in cls: return 35
            if 'product-audience' in cls: return 40
            if 'product-price' in cls: return 50
            if 'product-scope-line' in cls: return 60
            if 'product-turnaround' in cls: return 70
            if 'product-trust-line' in cls: return 80
            if 'actions' in cls: return 90
            if 'product-visual' in cls: return 100
            return 45
        for _, el in sorted(enumerate(elems), key=lambda t:(rank(t[1]), t[0])):
            shell.append(el.extract())

    mandatory = {hero, what, deliver, defined, disclosures, cta}
    optional = [s for s in sections if s not in mandatory]
    optional_wrap = soup.new_tag('div')
    optional_wrap['class'] = ['product-optional-modules']
    for s in optional:
        optional_wrap.append(s.extract())

    for child in list(main.children):
        if isinstance(child, Tag):
            child.extract()
    for node in (breadcrumb, hero, what, deliver, optional_wrap, defined, disclosures, cta, context):
        main.append(node.extract() if getattr(node, 'parent', None) is not None else node)

    p.write_text(str(soup), encoding='utf-8')

cssp = ROOT / 'assets' / 'hoc-service.css'
css = cssp.read_text(encoding='utf-8')
marker = '/* CANONICAL PRODUCT RENDER LOCK 2026-09-14 */'
block = '''\n\n/* CANONICAL PRODUCT RENDER LOCK 2026-09-14 */\nbody.canonical-product-page .product-hero{background:linear-gradient(180deg,#fff 0%,var(--mist) 100%);border-bottom:1px solid var(--stone)}\nbody.canonical-product-page .product-hero>.shell,body.canonical-product-page .product-section>.shell,body.canonical-product-page .service-context-nav,body.canonical-product-page .service-breadcrumbs{max-width:1180px;margin-left:auto;margin-right:auto;width:100%;box-sizing:border-box}\nbody.canonical-product-page .product-hero>.shell{padding:64px 56px 56px}\nbody.canonical-product-page .product-section{border-top:1px solid var(--stone);background:#fff}\nbody.canonical-product-page .product-section.alt{background:var(--mist)}\nbody.canonical-product-page .product-section>.shell{padding:54px 56px}\nbody.canonical-product-page .product-section h2{max-width:860px;margin-top:0}\nbody.canonical-product-page .recognition-grid,body.canonical-product-page .deliverable-groups{width:100%;max-width:980px}\nbody.canonical-product-page .service-facts{max-width:900px}\nbody.canonical-product-page .hoc-accordion-group{max-width:940px}\nbody.canonical-product-page .cta-panel{display:flex;align-items:center;justify-content:space-between;gap:32px}\nbody.canonical-product-page .product-optional-modules:empty{display:none}\nbody.canonical-product-page .product-optional-modules>.product-section{border-top:1px solid var(--stone)}\n@media(max-width:760px){body.canonical-product-page .product-hero>.shell,body.canonical-product-page .product-section>.shell{padding:44px 24px}body.canonical-product-page .cta-panel{display:block}body.canonical-product-page .cta-panel .button{margin-top:18px}}\n'''
if marker not in css:
    cssp.write_text(css + block, encoding='utf-8')

print(f'Canonical rendered template applied to {len(routes)} product pages.')
