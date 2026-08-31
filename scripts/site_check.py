from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BUILD = "customer1-house-20260831a"
HTML_NAMES = ("index.html", "website-release-assurance.html", "catalogue.html", "privacy.html", "terms.html", "404.html")
HTML_FILES = [ROOT / name for name in HTML_NAMES]
EXPECTED_STYLE = f"assets/hoc-grand-house.css?v={BUILD}"
EXPECTED_SCRIPTS = [f"assets/hoc-experience.js?v={BUILD}", f"assets/hoc-diagnostics.js?v={BUILD}"]
STYLE_ENTRY = ROOT / "assets" / "hoc-grand-house.css"
STYLE_BASE = ROOT / "assets" / "hoc-grand-house-base.css"
EXPECTED_BASE_IMPORT = f'@import url("hoc-grand-house-base.css?v={BUILD}");'
BANNED_PUBLIC_PHRASES = ("£5", "external cleared revenue", "52-hive", "52 hive", "engine architecture", "maturity score", "acquisition gate", "award-winning", "world-class", "fortune 500", "ai-powered", "waylight atlantic", "alanwpgallagher.info", "building, owning and operating")
OBSOLETE_NAME_PARTS = ("qa-run", "run10", "run13", "trigger")

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.hrefs=[]; self.scripts=[]; self.styles=[]; self.labels_for=set(); self.controls=set()
        self.forms=[]; self.lang=None; self.viewport=False; self.robots=None; self.csp=None; self.build=None
        self.title_count=0; self.h1_count=0; self.descriptions=[]; self.inline_scripts=0
    def handle_starttag(self, tag, attrs_list):
        attrs={k:(v or "") for k,v in attrs_list}
        if tag=="html": self.lang=attrs.get("lang")
        elif tag=="title": self.title_count+=1
        elif tag=="h1": self.h1_count+=1
        elif tag=="meta":
            if attrs.get("name")=="viewport": self.viewport=bool(attrs.get("content"))
            elif attrs.get("name")=="robots": self.robots=attrs.get("content")
            elif attrs.get("name")=="description": self.descriptions.append(attrs.get("content"))
            elif attrs.get("name")=="hoc-build": self.build=attrs.get("content")
            elif attrs.get("http-equiv","").lower()=="content-security-policy": self.csp=attrs.get("content")
        if "id" in attrs:
            if attrs["id"] in self.ids: raise AssertionError(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag=="a" and attrs.get("href"): self.hrefs.append(attrs["href"])
        elif tag=="script":
            if attrs.get("src"): self.scripts.append(attrs["src"])
            else: self.inline_scripts += 1
        elif tag=="link" and attrs.get("rel")=="stylesheet" and attrs.get("href"): self.styles.append(attrs["href"])
        elif tag=="label" and attrs.get("for"): self.labels_for.add(attrs["for"])
        elif tag in {"input","textarea","select"} and attrs.get("id"):
            if attrs.get("type","").lower()!="hidden": self.controls.add(attrs["id"])
        elif tag=="form": self.forms.append(attrs)

def fail(message): raise SystemExit(f"FAIL: {message}")
def parse(path):
    parser=PageParser(); text=path.read_text(encoding="utf-8")
    try: parser.feed(text)
    except AssertionError as exc: fail(f"{path.name}: {exc}")
    lowered=text.lower()
    for phrase in BANNED_PUBLIC_PHRASES:
        if phrase.lower() in lowered: fail(f"{path.name}: banned internal/unsupported phrase present: {phrase}")
    return parser

for path in ROOT.rglob("*"):
    if path.is_file():
        rel=path.relative_to(ROOT).as_posix().lower()
        if any(part in rel for part in OBSOLETE_NAME_PARTS): fail(f"obsolete/review-specific file shipped: {rel}")

required=[*HTML_FILES, STYLE_ENTRY, STYLE_BASE, ROOT/"assets"/"hoc-experience.js", ROOT/"assets"/"hoc-diagnostics.js", ROOT/"assets"/"hoc-mark.svg", ROOT/"robots.txt"]
for item in required:
    if not item.exists(): fail(f"missing {item.relative_to(ROOT)}")

pages={}
for html in HTML_FILES:
    p=parse(html); pages[html.resolve()]=p
    if p.lang!="en-GB": fail(f"{html.name}: lang")
    if p.title_count!=1 or p.h1_count!=1: fail(f"{html.name}: expected one title/h1")
    if not p.viewport: fail(f"{html.name}: viewport")
    if p.robots!="noindex,nofollow": fail(f"{html.name}: containment")
    if p.build!=BUILD: fail(f"{html.name}: build {p.build}")
    if not p.csp or "object-src 'none'" not in p.csp or "base-uri 'self'" not in p.csp or "connect-src 'none'" not in p.csp or "form-action 'none'" not in p.csp: fail(f"{html.name}: CSP")
    if p.styles != [EXPECTED_STYLE]: fail(f"{html.name}: style {p.styles}")
    if p.scripts != EXPECTED_SCRIPTS: fail(f"{html.name}: scripts {p.scripts}")
    if p.inline_scripts: fail(f"{html.name}: inline scripts present")
    if len(p.descriptions)!=1 or not p.descriptions[0].strip(): fail(f"{html.name}: descriptive meta missing")
    missing=p.controls-p.labels_for
    if missing: fail(f"{html.name}: unlabelled controls {sorted(missing)}")
    if p.forms: fail(f"{html.name}: unexpected form; current contact route is mailto/Gmail")

def local_target(base, href):
    parsed=urlparse(href)
    if parsed.scheme in {"mailto","tel"}: return None
    if parsed.scheme or parsed.netloc:
        if parsed.scheme!="https": fail(f"{base.name}: non-https external {href}")
        return None
    return (base.parent/(parsed.path or base.name)).resolve(), parsed.fragment or None

for base,p in pages.items():
    for href in p.hrefs:
        info=local_target(base,href)
        if info is None: continue
        target,frag=info
        if target.suffix=="": target=target/"index.html"
        if not target.exists(): fail(f"{base.name}: broken {href}")
        if frag and target.suffix==".html":
            tp=pages.get(target.resolve()) or parse(target)
            if frag not in tp.ids: fail(f"{base.name}: broken anchor {href}")

idx=pages[(ROOT/"index.html").resolve()]
for rid in ("work","standard","house","contact"):
    if rid not in idx.ids: fail(f"index missing #{rid}")
text=(ROOT/"index.html").read_text(encoding="utf-8")
for token in ("house-field","motion-control","chapter-rail","Website Release Assurance","£149","Sales Department"):
    if token not in text: fail(f"index missing mature-House structure/content {token}")
if "formspree" in text.lower(): fail("index: obsolete Formspree route present")
if 'class="card' in text or ' class="card' in text: fail("generic card component introduced")
service=(ROOT/"website-release-assurance.html").read_text(encoding="utf-8")
for token in ("£149","2 working days","RELEASE WITH ACCEPTED EXCEPTIONS","penetration testing","invoice on delivery"):
    if token not in service: fail(f"service page missing controlled commercial fact: {token}")
entry_css=STYLE_ENTRY.read_text(encoding="utf-8")
base_css=STYLE_BASE.read_text(encoding="utf-8")
if entry_css.count("@import")!=1 or not entry_css.lstrip().startswith(EXPECTED_BASE_IMPORT): fail("CSS entry must import exactly the versioned local Grand House base")
if "http://" in entry_css or "https://" in entry_css or "http://" in base_css or "https://" in base_css or "@import" in base_css: fail("CSS external or nested dependency")
css=base_css+"\n"+entry_css
for token in ("--gold:","--burgundy:",".house-field",".offer-stage",".contact-routes",".service-body","prefers-reduced-motion","@media(max-width:560px)"):
    if token not in css: fail(f"CSS missing {token}")
js=(ROOT/"assets"/"hoc-experience.js").read_text(encoding="utf-8")
for token in ("prefers-reduced-motion","IntersectionObserver","requestAnimationFrame","pointermove"):
    if token not in js: fail(f"experience missing {token}")
if "fetch(" in js or "localStorage" in js or "sessionStorage" in js or "document.cookie" in js: fail("experience introduced network/storage")
robots=(ROOT/"robots.txt").read_text(encoding="utf-8")
if "Disallow: /" not in robots: fail("robots containment")
print("PASS: Customer 1 mature-House static integrity, real service, Gmail contact routing, noindex containment and local interaction architecture checks")
