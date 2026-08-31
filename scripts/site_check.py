from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BUILD = "ce2-run15-20260831a"
HTML_NAMES = ("index.html", "catalogue.html", "privacy.html", "terms.html", "404.html")
HTML_FILES = [ROOT / name for name in HTML_NAMES]
EXPECTED_STYLE = f"assets/hoc-public.css?v={BUILD}"
EXPECTED_SCRIPT = f"assets/hoc-diagnostics.js?v={BUILD}"
BANNED_PUBLIC_PHRASES = (
    "£5",
    "external cleared revenue",
    "52-hive",
    "52 hive",
    "engine architecture",
    "maturity score",
    "acquisition gate",
    "award-winning",
    "world-class",
    "fortune 500",
    "ai-powered",
    "AI Release QA",
    "Document-to-Decision",
    "Hard-to-Find Parts",
    "Niche Tender Intelligence",
    "Product Data Quality & Catalogue Enrichment",
    "Website Quality Watch",
)
OBSOLETE_NAME_PARTS = ("qa-run", "run10", "run13", "trigger")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.labels_for: set[str] = set()
        self.controls: set[str] = set()
        self.forms: list[dict[str, str]] = []
        self.lang: str | None = None
        self.viewport = False
        self.robots: str | None = None
        self.csp: str | None = None
        self.build: str | None = None
        self.title_count = 0
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k: (v or "") for k, v in attrs_list}
        if tag == "html":
            self.lang = attrs.get("lang")
        elif tag == "title":
            self.title_count += 1
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            if attrs.get("name") == "viewport":
                self.viewport = bool(attrs.get("content"))
            elif attrs.get("name") == "robots":
                self.robots = attrs.get("content")
            elif attrs.get("name") == "hoc-build":
                self.build = attrs.get("content")
            elif attrs.get("http-equiv", "").lower() == "content-security-policy":
                self.csp = attrs.get("content")
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise AssertionError(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])
        elif tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        elif tag == "link" and attrs.get("rel") == "stylesheet" and attrs.get("href"):
            self.styles.append(attrs["href"])
        elif tag == "label" and attrs.get("for"):
            self.labels_for.add(attrs["for"])
        elif tag in {"input", "textarea", "select"} and attrs.get("id"):
            if attrs.get("type", "").lower() != "hidden":
                self.controls.add(attrs["id"])
        elif tag == "form":
            self.forms.append(attrs)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse(path: Path) -> PageParser:
    parser = PageParser()
    text = path.read_text(encoding="utf-8")
    try:
        parser.feed(text)
    except AssertionError as exc:
        fail(f"{path.name}: {exc}")
    lowered = text.lower()
    for phrase in BANNED_PUBLIC_PHRASES:
        if phrase.lower() in lowered:
            fail(f"{path.name}: banned internal/unsupported phrase present: {phrase}")
    if "[service address]" in lowered or "[hoc public email]" in lowered or "[legal name]" in lowered:
        fail(f"{path.name}: raw release placeholder present")
    return parser


for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix().lower()
    if any(part in rel for part in OBSOLETE_NAME_PARTS):
        fail(f"obsolete/review-specific file shipped: {rel}")

required_files = [
    *HTML_FILES,
    ROOT / "assets" / "hoc-public.css",
    ROOT / "assets" / "hoc-mark.svg",
    ROOT / "assets" / "hoc-diagnostics.js",
    ROOT / "robots.txt",
]
for required in required_files:
    if not required.exists():
        fail(f"missing required public/release file: {required.relative_to(ROOT)}")

pages: dict[Path, PageParser] = {}
for html_file in HTML_FILES:
    parser = parse(html_file)
    pages[html_file.resolve()] = parser
    if parser.lang != "en-GB":
        fail(f"{html_file.name}: expected lang=en-GB")
    if parser.title_count != 1:
        fail(f"{html_file.name}: expected exactly one title element")
    if parser.h1_count != 1:
        fail(f"{html_file.name}: expected exactly one h1")
    if not parser.viewport:
        fail(f"{html_file.name}: missing viewport meta")
    if parser.robots != "noindex,nofollow":
        fail(f"{html_file.name}: containment meta changed")
    if parser.build != BUILD:
        fail(f"{html_file.name}: wrong or missing build identity: {parser.build}")
    if not parser.csp or "object-src 'none'" not in parser.csp or "base-uri 'self'" not in parser.csp:
        fail(f"{html_file.name}: CSP baseline missing")
    if parser.styles != [EXPECTED_STYLE]:
        fail(f"{html_file.name}: expected one current stylesheet, got {parser.styles}")
    if parser.scripts != [EXPECTED_SCRIPT]:
        fail(f"{html_file.name}: expected diagnostics-only script, got {parser.scripts}")
    missing_labels = parser.controls - parser.labels_for
    if missing_labels:
        fail(f"{html_file.name}: unlabelled controls: {sorted(missing_labels)}")


def local_target(base: Path, href: str) -> tuple[Path, str | None] | None:
    parsed = urlparse(href)
    if parsed.scheme in {"mailto", "tel"}:
        return None
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https":
            fail(f"{base.name}: external link is not https: {href}")
        return None
    file_part = parsed.path or base.name
    return (base.parent / file_part).resolve(), parsed.fragment or None


for base, parser in pages.items():
    for href in parser.hrefs:
        target_info = local_target(base, href)
        if target_info is None:
            continue
        target, fragment = target_info
        if target.suffix == "":
            target = target / "index.html"
        if not target.exists():
            fail(f"{base.name}: broken local link {href}")
        if fragment and target.suffix == ".html":
            target_parser = pages.get(target.resolve()) or parse(target)
            if fragment not in target_parser.ids:
                fail(f"{base.name}: broken anchor {href}")

index_path = (ROOT / "index.html").resolve()
index = pages[index_path]
if len(index.forms) != 1:
    fail(f"index.html: expected one contact form, got {len(index.forms)}")
form = index.forms[0]
if form.get("action") != "https://formspree.io/f/mgvgrgvb":
    fail("index.html: unexpected Formspree endpoint")
if form.get("method", "").lower() != "post":
    fail("index.html: contact form must use POST")
for name in ("catalogue.html", "privacy.html", "terms.html", "404.html"):
    if pages[(ROOT / name).resolve()].forms:
        fail(f"{name}: unexpected form present")

for required_id in ("house", "portfolio", "contact"):
    if required_id not in index.ids:
        fail(f"index.html: missing core House destination #{required_id}")

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
if "hero-stage" not in index_text or "principle-list" not in index_text or "portfolio-callout" not in index_text:
    fail("index.html: flagship House narrative structure missing")
if "hoc-silhouette.svg" in index_text or "hero-silhouette" in index_text:
    fail("index.html: rejected Run 14 silhouette direction has returned")
if "class=\"card" in index_text or " class=\"card" in index_text:
    fail("index.html: generic card component introduced into flagship narrative")

css = (ROOT / "assets" / "hoc-public.css").read_text(encoding="utf-8")
if "http://" in css or "https://" in css or "@import" in css:
    fail("hoc-public.css: external/imported design dependency introduced")
for token in ("--gold:", "--burgundy:", ".hero-stage", ".ledger-row", "prefers-reduced-motion"):
    if token not in css:
        fail(f"hoc-public.css: expected flagship/accessibility token missing: {token}")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if "Disallow: /" not in robots:
    fail("robots.txt containment changed")

print("PASS: Run 15 House static integrity, containment, public-truth and flagship-structure checks")
