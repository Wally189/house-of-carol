from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / name for name in ("index.html", "catalogue.html", "privacy.html", "terms.html", "404.html")]
BANNED_PUBLIC_PHRASES = ("award-winning", "world-class", "ai-powered", "fortune 500")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.scripts: list[str] = []
        self.labels_for: set[str] = set()
        self.inputs: set[str] = set()
        self.title = False
        self.lang = None
        self.viewport = False
        self.robots = None
        self.csp = None
        self.forms: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k: (v or "") for k, v in attrs_list}
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.title = True
        if tag == "meta":
            if attrs.get("name") == "viewport":
                self.viewport = bool(attrs.get("content"))
            if attrs.get("name") == "robots":
                self.robots = attrs.get("content")
            if attrs.get("http-equiv", "").lower() == "content-security-policy":
                self.csp = attrs.get("content")
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise AssertionError(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        if tag == "label" and attrs.get("for"):
            self.labels_for.add(attrs["for"])
        if tag in {"input", "textarea", "select"} and attrs.get("id"):
            input_type = attrs.get("type", "")
            if input_type != "hidden":
                self.inputs.add(attrs["id"])
        if tag == "form":
            self.forms.append(attrs)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    text = path.read_text(encoding="utf-8")
    try:
        parser.feed(text)
    except AssertionError as exc:
        fail(f"{path.name}: {exc}")
    for phrase in BANNED_PUBLIC_PHRASES:
        if phrase in text.lower():
            fail(f"{path.name}: unsupported prestige phrase present: {phrase}")
    return parser


def local_target(base: Path, href: str) -> tuple[Path, str | None] | None:
    if href.startswith(("mailto:", "tel:")):
        return None
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https":
            fail(f"{base.name}: external link is not https: {href}")
        return None
    file_part = parsed.path or base.name
    target = (base.parent / file_part).resolve()
    return target, parsed.fragment or None


pages: dict[Path, PageParser] = {}
for html_file in HTML_FILES:
    if not html_file.exists():
        fail(f"missing public page: {html_file.name}")
    parser = parse(html_file)
    pages[html_file.resolve()] = parser
    if parser.lang != "en-GB":
        fail(f"{html_file.name}: expected lang=en-GB")
    if not parser.title:
        fail(f"{html_file.name}: missing title")
    if not parser.viewport:
        fail(f"{html_file.name}: missing viewport meta")
    if parser.robots != "noindex,nofollow":
        fail(f"{html_file.name}: containment meta changed")
    if not parser.csp or "object-src 'none'" not in parser.csp or "base-uri 'self'" not in parser.csp:
        fail(f"{html_file.name}: CSP baseline missing")
    missing_labels = parser.inputs - parser.labels_for
    if missing_labels:
        fail(f"{html_file.name}: unlabelled controls: {sorted(missing_labels)}")
    for script in parser.scripts:
        target = (html_file.parent / script).resolve()
        if not target.exists():
            fail(f"{html_file.name}: missing script: {script}")

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

catalogue = pages[(ROOT / "catalogue.html").resolve()]
if not catalogue.forms:
    fail("catalogue.html: contact form missing")
form = catalogue.forms[0]
if form.get("action") != "https://formspree.io/f/mgvgrgvb":
    fail("catalogue.html: unexpected Formspree endpoint")
if form.get("method", "").lower() != "post":
    fail("catalogue.html: contact form must use POST")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if "Disallow: /" not in robots:
    fail("robots.txt containment changed")

print("PASS: static site integrity checks")
