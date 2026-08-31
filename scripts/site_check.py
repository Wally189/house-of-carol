from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BUILD = "deep-human-house-20260831a"
HTML_NAMES = ("index.html", "catalogue.html", "privacy.html", "terms.html", "404.html")
HTML_FILES = [ROOT / name for name in HTML_NAMES]
EXPECTED_STYLE = f"assets/hoc-house-2.css?v={BUILD}"
STYLE = ROOT / "assets" / "hoc-house-2.css"
BANNED_PUBLIC_PHRASES = (
    "52-hive", "52 hive", "engine architecture", "maturity score", "acquisition gate",
    "world-class", "game-changing", "industry-leading", "cutting-edge", "transformational",
    "cross-functional synergies", "future-ready architecture", "the threshold", "grand house",
    "ai-powered", "waylight atlantic", "alanwpgallagher.info", "£5"
)
BANNED_AI_SLUDGE = ("delve into", "vibrant tapestry", "seamless journey", "unlock the power", "ever-evolving landscape")

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
    for phrase in (*BANNED_PUBLIC_PHRASES,*BANNED_AI_SLUDGE):
        if phrase.lower() in lowered: fail(f"{path.name}: banned inward/hype/sludge phrase present: {phrase}")
    return parser

required=[*HTML_FILES, STYLE, ROOT/"assets"/"hoc-mark.svg", ROOT/"robots.txt"]
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
    if not p.csp or "object-src 'none'" not in p.csp or "base-uri 'self'" not in p.csp or "connect-src 'none'" not in p.csp or "script-src 'none'" not in p.csp or "form-action 'none'" not in p.csp: fail(f"{html.name}: CSP")
    if p.styles != [EXPECTED_STYLE]: fail(f"{html.name}: style {p.styles}")
    if p.scripts or p.inline_scripts: fail(f"{html.name}: scripts present in static candidate")
    if len(p.descriptions)!=1 or not p.descriptions[0].strip(): fail(f"{html.name}: descriptive meta missing")
    if p.forms: fail(f"{html.name}: public form present during simulation-only mode")
    missing=p.controls-p.labels_for
    if missing: fail(f"{html.name}: unlabelled controls {sorted(missing)}")

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
for rid in ("work","method","contact"):
    if rid not in idx.ids: fail(f"index missing #{rid}")
index_text=(ROOT/"index.html").read_text(encoding="utf-8").lower()
for required_text in ("useful work, done properly", "website release checks", "data clean-up and structure", "workflow fixes", "research for a decision", "07933 657446"):
    if required_text not in index_text: fail(f"index missing buyer-useful content: {required_text}")
if 'class="card' in index_text or ' class="card' in index_text: fail("generic card component introduced")
css=STYLE.read_text(encoding="utf-8")
if "http://" in css or "https://" in css or "@import" in css: fail("CSS external/nested dependency")
for token in ("--paper:","--wine:","prefers-reduced-motion","@media(max-width:820px)",":focus-visible"):
    if token not in css: fail(f"CSS missing {token}")
robots=(ROOT/"robots.txt").read_text(encoding="utf-8")
if "Disallow: /" not in robots: fail("robots containment")
print("PASS: Human House static integrity, containment, buyer-first content, no-form control and local design checks")
