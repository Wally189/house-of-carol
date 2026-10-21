#!/usr/bin/env python3
"""Fail-closed post-build HOC SEO policy.

Preflight all files and directives before any proposed indexability is written.
Refuses to silently overwrite new robots or sitemap policy introduced upstream.
"""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HOST = 'https://houseofcarol.co.uk'
INDEXABLE = (
    'index.html', 'how-it-works.html', 'catalogue.html', 'about.html', 'contact.html',
    'catalogue-operations.html', 'catalogue-ai-digital.html',
    'catalogue-commercial.html', 'catalogue-learning.html',
    'catalogue-research.html', 'catalogue-charity-public.html',
    'catalogue-church-parish.html',
)
META = re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']\s*/?>', re.I)
CANONICAL = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']\s*/?>', re.I)
BASE_ROBOTS = 'User-agent: *\nDisallow:\n'
TARGET_ROBOTS = BASE_ROBOTS + '\nSitemap: ' + HOST + '/sitemap.xml\n'


def canonical(name):
    return HOST + ('/' if name == 'index.html' else '/' + name.removesuffix('.html'))


def make_xml():
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    root = ET.Element('{' + ns + '}urlset')
    for name in INDEXABLE:
        ET.SubElement(ET.SubElement(root, '{' + ns + '}url'), '{' + ns + '}loc').text = canonical(name)
    ET.indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode') + '\n'


def apply(root):
    root = Path(root)
    pages = sorted(root.glob('*.html')) + sorted((root / 'qa').glob('*.html'))
    proposed = {}
    held = []
    for page in pages:
        rel = page.relative_to(root).as_posix()
        raw = page.read_text(encoding='utf-8')
        markers = list(META.finditer(raw))
        if len(markers) != 1:
            label = 'held route ' if rel not in INDEXABLE else ''
            raise ValueError(rel + ': ' + label + 'ambiguous/missing robots meta; fail closed')
        directive = markers[0].group(1).replace(' ', '').lower()
        if rel not in INDEXABLE:
            if 'noindex' not in directive.split(','):
                raise ValueError(rel + ': held route missing unambiguous robots noindex meta')
            held.append(rel)
            continue
        if directive not in ('noindex,nofollow', 'index,follow'):
            raise ValueError(rel + ': robots meta unexpectedly changed; fail closed')
        raw = raw[:markers[0].start()] + '<meta name="robots" content="index,follow">' + raw[markers[0].end():]
        links = list(CANONICAL.finditer(raw))
        if len(links) > 1 or (links and links[0].group(1) != canonical(rel)):
            raise ValueError(rel + ': conflicting canonical; fail closed')
        if not links:
            head = re.search(r'</head\s*>', raw, re.I)
            if not head:
                raise ValueError(rel + ': head missing; fail closed')
            raw = raw[:head.start()] + '<link rel="canonical" href="' + canonical(rel) + '">\n' + raw[head.start():]
        proposed[rel] = raw
    if set(proposed) != set(INDEXABLE):
        raise ValueError('Incomplete proposed public route set: fail closed')
    robots = root / 'robots.txt'
    current_robots = robots.read_text(encoding='utf-8').replace('\r\n', '\n')
    if current_robots not in (BASE_ROBOTS, TARGET_ROBOTS):
        raise ValueError('robots.txt changed from approved baseline: fail closed')
    sitemap = root / 'sitemap.xml'
    desired_xml = make_xml()
    if sitemap.exists() and sitemap.read_text(encoding='utf-8') != desired_xml:
        raise ValueError('Pre-existing sitemap differs from 12-page release scope: fail closed')
    for rel, content in proposed.items():
        (root / rel).write_text(content, encoding='utf-8')
    robots.write_text(TARGET_ROBOTS, encoding='utf-8')
    sitemap.write_text(desired_xml, encoding='utf-8')
    print(f'PASS: SEO build policy {len(INDEXABLE)} indexable, {len(held)} held pages')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    apply(p.parse_args().root)
