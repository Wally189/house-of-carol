from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = [
'ai-data-use-rules-sprint.html','ai-policy-and-sop-implementation-service.html','responsible-ai-workplace-training.html','role-based-ai-skills-workshop.html','ai-leadership-and-management-workshop.html','ai-workflow-opportunity-review.html','ai-workflow-implementation-sprint.html','ai-tool-and-account-governance-review.html','ai-vendor-tool-selection-review.html','independent-document-review.html','ai-operating-model-and-governance-blueprint.html','ai-adoption-support-retainer.html','no-code-ai-automation-implementation.html','business-knowledge-base-and-ai-retrieval-setup.html','process-design-sprint.html','shared-drive-cleanup.html','management-information-and-kpi-setup.html','customer-journey-and-service-operations-review.html','customer-support-knowledge-base-build.html','business-continuity-and-operational-readiness-pack.html','decision-rights-and-governance-review.html','complaints-and-redress-process-design.html','evidence-and-marketing-claim-substantiation-review.html','tender-review.html','tender-readiness-and-bid-evidence-library.html','public-procurement-opportunity-monitoring.html','invoice-to-cash-process-setup.html','cash-flow-and-financial-operations-setup.html','supplier-and-purchasing-process-setup.html','bespoke-organisational-training-design.html','assessment-and-competency-framework-design.html','internal-academy-learning-pathway-design.html','microlearning-and-scenario-assessment-packs.html','research-briefing.html','training-quality-review.html','church-and-parish-grant-funding-research.html','church-grant-application-development-support.html','church-building-funding-and-maintenance-roadmap.html','parish-operations-and-administration-improvement.html','parish-digital-and-ai-governance-starter-service.html','parish-communications-service.html','charity-ai-governance-pack-and-implementation.html','charity-cyber-and-digital-governance-readiness-review.html','charity-governance-and-trustee-information-pack-review.html','public-sector-decision-governance-review.html','committee-board-paper-quality-review.html','public-sector-sop-and-process-modernisation.html','consultation-and-evidence-synthesis-service.html','evidence-based-executive-briefing-service.html','b2b-charity-newsletter-production.html','explainer-and-thought-leadership-production.html','research-monitoring-horizon-scanning-subscription.html','website-completion-sprint.html']
CASE_PAGES = ['case-study-' + Path(p).stem + '.html' for p in PRODUCTS]
def fail(msg): raise SystemExit('FAIL: ' + msg)
index = ROOT / 'case-studies.html'
if not index.exists(): fail('case-studies.html missing')
index_text = index.read_text(encoding='utf-8')
links = re.findall(r'<a class="case-study-link" href="([^"]+)">', index_text)
if len(links) != 53 or len(set(links)) != 53: fail(f'case study index expected 53 unique routes, found {len(links)}/{len(set(links))}')
if set(links) != set(CASE_PAGES): fail('case study index route set differs from current product set')
h1s = set()
for product, case in zip(PRODUCTS, CASE_PAGES):
    path = ROOT / case
    if not path.exists(): fail('missing ' + case)
    text = path.read_text(encoding='utf-8'); low = text.lower()
    required = ['lang="en-GB"','name="viewport"','name="robots" content="noindex,nofollow"',"script-src 'none'",'class="skip" href="#main"','id="main"','composite illustration, not a real customer or claimed result.',f'href="{product}"','href="case-studies.html"','href="catalogue.html"','class="case-study-hero-visual"']
    for marker in required:
        if marker not in text and marker.lower() not in low: fail(case + ': missing ' + marker)
    if re.search(r'<script\b', text, re.I): fail(case + ': script present')
    if re.search(r'\sstyle\s*=', text, re.I): fail(case + ': inline style present')
    h = re.findall(r'<h1[^>]*>(.*?)</h1>', text, re.I | re.S)
    if len(h) != 1: fail(case + ': expected one H1')
    plain = re.sub(r'<[^>]+>', ' ', h[0]); plain = re.sub(r'\s+', ' ', plain).strip()
    if plain in h1s: fail('duplicate case-study H1: ' + plain)
    h1s.add(plain)
    ptext = (ROOT / product).read_text(encoding='utf-8')
    if f'href="{case}"' not in ptext: fail(product + ': matching case-study route not injected')
if index_text.count('class="case-study-card"') != 53: fail('case study index card count')
if index_text.count('class="case-family-head"') != 7: fail('case study index family count')
if '53 services · 53 separate illustrations' not in index_text: fail('case study index current-count statement missing')
if 'not testimonials' not in index_text.lower() or 'invented customer results' not in index_text.lower(): fail('case study index evidence disclosure missing')
catalogue = (ROOT / 'catalogue.html').read_text(encoding='utf-8')
if 'href="case-studies.html"' not in catalogue: fail('catalogue does not route to case-study index')
print('PASS: 53 distinct product pages each have a separate, clearly illustrative case-study route; case index, reciprocal navigation, evidence disclosure and containment checks pass')
