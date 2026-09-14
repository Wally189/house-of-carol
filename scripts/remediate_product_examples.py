from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "ai-data-use-rules-sprint.html": [
        ("Where examples are useful, we ask for workflow descriptions and synthetic, anonymised or redacted material wherever possible rather than unnecessary raw information.", "We ask for workflow descriptions and synthetic, anonymised or redacted material wherever possible rather than unnecessary raw information."),
    ],
    "role-based-ai-skills-workshop.html": [
        ("Participants work through representative tasks with decreasing support rather than only hearing examples or prompt tips.", "Participants work through representative tasks with decreasing support rather than only hearing generic prompt tips."),
        ("safe examples or enough context for us to create synthetic or redacted exercises.", "safe source material or enough context for us to create synthetic or redacted exercises."),
    ],
    "ai-workflow-opportunity-review.html": [
        ("Known information categories and material dependencies. Where examples are useful, synthetic, anonymised or appropriately redacted material is the default.", "Known information categories and material dependencies. Synthetic, anonymised or appropriately redacted material is the default."),
    ],
    "process-design-sprint.html": [
        ("documents, screenshots or examples", "documents, screenshots or source material"),
        ("Redact or anonymise examples where possible.", "Redact or anonymise sensitive material where possible."),
        ("<p>The example below is illustrative, not a customer case study.</p>", ""),
    ],
    "business-continuity-and-operational-readiness-pack.html": [
        ("This is a new service, so House of Carol does not yet claim live customer case-study results or proven recovery outcomes.", "This is a new service, so House of Carol does not yet claim live customer results or proven recovery outcomes."),
        ("<p>The Bramble Row example is fictional and is included only to show how the service is intended to work.</p>", ""),
    ],
    "decision-rights-and-governance-review.html": [
        ("<li>Examples of the recurring decisions in scope.</li>", "<li>Records or descriptions of the recurring decisions in scope.</li>"),
    ],
    "complaints-and-redress-process-design.html": [
        ("<p>No legal correctness, regulator acceptance, complaint result, remedy or measured customer benefit is guaranteed. The worked example on this page is fictional and illustrative, not customer proof.</p>", "<p>No legal correctness, regulator acceptance, complaint result, remedy or measured customer benefit is guaranteed.</p>"),
    ],
    "tender-readiness-and-bid-evidence-library.html": [
        ("case-study/evidence templates", "evidence templates"),
        ("no invented qualification, case study or performance claim", "no invented qualification or performance claim"),
        ("<article class=\"product-card\"><h3>Case-study structure</h3><p>A template for evidence-based case studies without invention.</p></article>", "<article class=\"product-card\"><h3>Evidence structure</h3><p>A template for structured supporting evidence without invention.</p></article>"),
        ("<p>No invented qualifications, case studies or performance evidence.</p>", "<p>No invented qualifications or performance evidence.</p>"),
    ],
    "parish-digital-and-ai-governance-starter-service.html": [
        ("A practical briefing that explains the rules through parish-relevant examples without pretending to replace specialist advice.", "A practical briefing that explains the rules using parish-relevant workflows without pretending to replace specialist advice."),
    ],
}

DETAIL_BLOCKS = {
    "business-continuity-and-operational-readiness-pack.html": "<summary>Can you give an example?</summary>",
}

SECTION_BLOCKS = {
    "shared-drive-cleanup.html": "<h2>Illustrative example</h2>",
    "complaints-and-redress-process-design.html": "<h2>A worked example</h2>",
    "evidence-and-marketing-claim-substantiation-review.html": "<h2>A worked example</h2>",
    "management-information-and-kpi-setup.html": 'class="product-section worked-example-promo"',
    "customer-journey-and-service-operations-review.html": 'class="product-section worked-example-promo"',
    "decision-rights-and-governance-review.html": 'class="product-section worked-example-promo"',
}

ARTICLE_BLOCKS = {
    "process-design-sprint.html": "<h3>A typical handover problem</h3>",
}

changed = set()


def replace_once(text, old, new, filename):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{filename}: expected exactly one occurrence of {old!r}; found {count}")
    return text.replace(old, new, 1)


def remove_enclosing_block(text, marker, open_token, close_token, filename, max_chars):
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"{filename}: expected exactly one marker {marker!r}; found {count}")
    marker_at = text.index(marker)
    start = text.rfind(open_token, 0, marker_at + 1)
    end_at = text.find(close_token, marker_at)
    if start < 0 or end_at < 0:
        raise RuntimeError(f"{filename}: could not resolve enclosing block for {marker!r}")
    end = end_at + len(close_token)
    removed = text[start:end]
    if len(removed) > max_chars:
        raise RuntimeError(f"{filename}: refusing over-broad removal of {len(removed)} chars around {marker!r}")
    if marker not in removed or removed.count(open_token) != 1:
        raise RuntimeError(f"{filename}: refusing ambiguous block removal around {marker!r}")
    return text[:start] + text[end:]


for filename, pairs in REPLACEMENTS.items():
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in pairs:
        text = replace_once(text, old, new, filename)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.add(filename)

for filename, marker in DETAIL_BLOCKS.items():
    path = ROOT / filename
    text = remove_enclosing_block(path.read_text(encoding="utf-8"), marker, "<details", "</details>", filename, 7000)
    path.write_text(text, encoding="utf-8")
    changed.add(filename)

for filename, marker in SECTION_BLOCKS.items():
    path = ROOT / filename
    text = remove_enclosing_block(path.read_text(encoding="utf-8"), marker, "<section", "</section>", filename, 9000)
    path.write_text(text, encoding="utf-8")
    changed.add(filename)

for filename, marker in ARTICLE_BLOCKS.items():
    path = ROOT / filename
    text = remove_enclosing_block(path.read_text(encoding="utf-8"), marker, "<article", "</article>", filename, 5000)
    path.write_text(text, encoding="utf-8")
    changed.add(filename)

expected = {
    "ai-data-use-rules-sprint.html",
    "role-based-ai-skills-workshop.html",
    "ai-workflow-opportunity-review.html",
    "process-design-sprint.html",
    "shared-drive-cleanup.html",
    "management-information-and-kpi-setup.html",
    "customer-journey-and-service-operations-review.html",
    "business-continuity-and-operational-readiness-pack.html",
    "decision-rights-and-governance-review.html",
    "complaints-and-redress-process-design.html",
    "evidence-and-marketing-claim-substantiation-review.html",
    "tender-readiness-and-bid-evidence-library.html",
    "parish-digital-and-ai-governance-starter-service.html",
}
if changed != expected:
    raise RuntimeError(f"Changed-file set mismatch: expected {sorted(expected)}, got {sorted(changed)}")
print("Remediated exactly 13 product pages:")
for filename in sorted(changed):
    print(f"- {filename}")
