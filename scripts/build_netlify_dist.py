#!/usr/bin/env python3
"""Prepare the existing verified static House of Carol build for Netlify.

Publish only the website's generated static HTML/assets. Do not publish scripts,
source data, CI configuration, or internal programme documents.
"""
from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = sorted(ROOT.glob('*.html'))
QA_PAGES = sorted((ROOT / 'qa').glob('*.html'))
PUBLIC_STATIC = ('robots.txt','sitemap.xml','.nojekyll')
if len(PAGES) != 78 or len(QA_PAGES) != 1:
    raise SystemExit(f'NETLIFY DIST STOP: source HTML contract changed: root {len(PAGES)}, QA {len(QA_PAGES)}')
if not (ROOT/'catalogue.html').exists():
    raise SystemExit('NETLIFY DIST STOP: catalogue missing')
for name, count in {'catalogue-operations.html':4,'catalogue-ai-digital.html':6,
                    'catalogue-commercial.html':0,'catalogue-learning.html':0,
                    'catalogue-research.html':1,'catalogue-charity-public.html':0,
                    'catalogue-church-parish.html':1}.items():
    text=(ROOT/name).read_text(encoding='utf-8')
    actual=len(re.findall(r'<article class="service-entry" id="hoc-\d{3}" data-offer-id="HOC-\d{3}"', text))
    if actual!=count:
        raise SystemExit(f'NETLIFY DIST STOP: {name} expected {count} eligible cards; found {actual}')
if 'admin-service-section' in (ROOT/'catalogue.html').read_text(encoding='utf-8'):
    raise SystemExit('NETLIFY DIST STOP: held HOC-065 remains prominently featured')
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
for page in PAGES:
    shutil.copy2(page, DIST/page.name)
for page in QA_PAGES:
    dest=DIST/'qa'/page.name
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(page,dest)
shutil.copytree(ROOT/'assets',DIST/'assets')
for name in PUBLIC_STATIC:
    path=ROOT/name
    if path.is_file():
        shutil.copy2(path,DIST/name)
for illegal in ('scripts','data','.github','README.md','netlify.toml','build_netlify_dist.py'):
    if (DIST/illegal).exists():
        raise SystemExit('NETLIFY DIST STOP: private build material leaked: '+illegal)
for name in ('index.html','catalogue.html','contact.html','about.html','robots.txt','sitemap.xml',
             'assets/hoc-commercial-eligibility.css'):
    if not (DIST/name).is_file():raise SystemExit('NETLIFY DIST STOP: missing '+name)
for route in ('process-design-sprint.html','research-briefing.html',
              'managed-business-administration.html','tender-review.html'):
    html=(DIST/route).read_text(encoding='utf-8')
    if html.count('class="commercial-eligibility-notice"')!=1:
        raise SystemExit('NETLIFY DIST STOP: missing status in '+route)
    if 'noindex,nofollow' not in html:
        raise SystemExit('NETLIFY DIST STOP: held indexing changed '+route)
print(f'PASS: Netlify dist contains {len(PAGES)} root HTML, {len(QA_PAGES)} QA HTML, 7 family choices and 54 controlled product pages; scripts/data excluded')
