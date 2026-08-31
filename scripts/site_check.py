from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML_NAMES = ("index.html","services.html","how-we-work.html","about.html","privacy.html","terms.html","404.html")
HTML_FILES = [ROOT / name for name in HTML_NAMES]
EXPECTED_STYLE = "assets/hoc-rebuild.css"
STYLE = ROOT / "assets" / "hoc-rebuild.css"
BANNED_PUBLIC_PHRASES = (
    "52-hive","52 hive","engine architecture","maturity score","acquisition gate",
    "world-class","game-changing","industry-leading","cutting-edge","transformational",
    "cross-functional synergies","future-ready architecture","grand house","ai-powered",
    "waylight atlantic","alanwpgallagher.info","customer 000","runtime","330-function"
)
BANNED_AI_SLUDGE = ("delve into","vibrant tapestry","seamless journey","unlock the power","ever-evolving landscape")

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.hrefs=[]; self.scripts=[]; self.styles=[]; self.forms=[]
        self.lang=None; self.viewport=False; self.robots=None; self.csp=None
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
            elif attrs.get("http-equiv","").lower()=="content-security-policy": self.csp=attrs.get("content")
        if "id" in attrs:
            if attrs["id"] in self.ids: raise AssertionError(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag=="a" and attrs.get("href"): self.hrefs.append(attrs["href"])
        elif tag=="script":
            if attrs.get("src"): self.scripts.append(attrs["src"])
            else: self.inline_scripts += 1
        elif tag=="link" and attrs.get("rel")=="stylesheet" and attrs.get("href"): self.styles.append(attrs["href"])
        elif tag=="form": self.forms.append(attrs)

def fail(message): raise SystemExit(f"FAIL: {message}")
def parse(path):
    parser=PageParser(); text=path.read_text(encoding="utf-8")
    try: parser.feed(text)
    except AssertionError as exc: fail(f"{path.name}: {exc}")
    lowered=text.lower()
    for phrase in (*BANNED_PUBLIC_PHRASES,*BANNED_AI_SLUDGE):
        if phrase in lowered: fail(f"{path.name}: banned inward/hype/sludge phrase present: {phrase}")
    return parser

for item in [*HTML_FILES,STYLE,ROOT/"assets"/"hoc-mark.svg",ROOT/"robots.txt"]:
    if not item.exists(): fail(f"missing {item.relative_to(ROOT)}")

pages={}
for html in HTML_FILES:
    p=parse(html); pages[html.resolve()]=p
    if p.lang!="en-GB": fail(f"{html.name}: lang")
    if p.title_count!=1 or p.h1_count!=1: fail(f"{html.name}: expected one title/h1")
    if not p.viewport: fail(f"{html.name}: viewport")
    if p.robots!="noindex,nofollow": fail(f"{html.name}: containment")
    if not p.csp or "object-src 'none'" not in p.csp or "base-uri 'self'" not in p.csp: fail(f"{html.name}: CSP")
    if p.styles != [EXPECTED_STYLE]: fail(f"{html.name}: style {p.styles}")
    if p.scripts or p.inline_scripts: fail(f"{html.name}: scripts present in static preview")
    if len(p.descriptions)!=1 or not p.descriptions[0].strip(): fail(f"{html.name}: descriptive meta missing")

idx=(ROOT/"index.html").read_text(encoding="utf-8").lower()
for required_text in ("intelligence","judgement","impact","workflow implementation","website release assurance","controlled preview"):
    if required_text not in idx: fail(f"index missing current House content: {required_text}")
if 'class="card' in idx or ' class="card' in idx: fail("generic card component introduced")
css=STYLE.read_text(encoding="utf-8")
if "http://" in css or "https://" in css or "@import" in css: fail("CSS external/nested dependency")
for token in ("--carol:","--claret:","prefers-reduced-motion",":focus"):
    if token not in css: fail(f"CSS missing {token}")
robots=(ROOT/"robots.txt").read_text(encoding="utf-8")
if "Disallow: /" not in robots: fail("robots containment")
print("PASS: current House brand, containment, semantic integrity and no-sludge checks")
