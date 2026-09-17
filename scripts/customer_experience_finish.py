from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

META_REPLACEMENTS = (
    ('first-test research fee', 'research fee'), ('First-test research fee', 'Research fee'),
    ('indicative scope band', 'indicative range'), ('Final price is confirmed after scope fit.', 'We confirm the exact fee after checking what you need.'),
    ('scope fit', 'what you need'), ('bounded', 'focused'), ('Bounded', 'Focused'),
    ('first-test', 'initial'), ('First-test', 'Initial'), ('service unit', 'service'), ('Service unit', 'Service'),
    ('governance kernel', 'governance framework'), ('Governance kernel', 'Governance framework'),
    ('source universe', 'source set'), ('Source universe', 'Source set'),
    ('internal QA', 'quality review'), ('Internal QA', 'Quality review'), ('proprietor-approved', 'approved'), ('Proprietor-approved', 'Approved'),
)

PRODUCT_NAME_REPLACEMENTS = {
    'shared-drive-cleanup.html': (
        ('Shared Drive &amp; Document Cleanup', 'Document Control &amp; Knowledge-System Cleanup'),
        ('Shared Drive & Document Cleanup', 'Document Control & Knowledge-System Cleanup'),
    ),
    'management-information-and-kpi-setup.html': (
        ('Management Reporting Setup', 'Management Information & KPI Setup'),
    ),
}

PRODUCT_REMEDIATION = {
    'ai-policy-and-sop-implementation-service.html': {
        'promise': 'The service does not guarantee compliance, adoption or business outcomes. The customer remains responsible for its policy decisions and any legal, privacy, security or specialist approvals.',
    },
    'bespoke-organisational-training-design.html': {
        'scope': 'One defined learning-design project covering objectives, programme architecture, materials, practice, assessment planning and facilitator guidance.',
        'promise': 'The design does not guarantee learner performance or business outcomes and does not create an accredited qualification.',
    },
    'assessment-and-competency-framework-design.html': {
        'scope': 'One defined competency and assessment design covering the competency model, assessment criteria, evidence methods, moderation approach and scoring guidance.',
        'promise': 'The framework does not create an accredited qualification, licence or professional credential and does not guarantee learner or business outcomes.',
    },
    'internal-academy-learning-pathway-design.html': {
        'scope': 'One defined internal learning-pathway design covering curriculum architecture, pathways, modules, practice, assessment, governance and maintenance.',
        'promise': 'The design does not create an accredited qualification and does not guarantee learner performance or organisational outcomes.',
    },
    'microlearning-and-scenario-assessment-packs.html': {
        'scope': 'One commissioned learning project covering microlearning modules, workplace scenarios, answer rationales, assessment and facilitator or manager notes.',
        'promise': 'The pack does not create an accredited credential and does not guarantee learner performance or business outcomes.',
    },
    'training-quality-review.html': {
        'scope': 'One defined training-quality review covering design, learning method, assessment, accessibility and prioritised improvement actions.',
        'promise': 'The review does not guarantee learner performance, transfer into work, accreditation or business results. It assesses the training design and evidence within the agreed scope.',
    },
    'research-briefing.html': {
        'promise': 'The briefing does not guarantee a particular decision or business outcome. It explains what the available evidence supports, what remains uncertain and where specialist judgement may still be required.',
    },
    'evidence-based-executive-briefing-service.html': {
        'scope': 'One executive briefing on a defined subject, using an agreed current source set, with key developments, implications, uncertainties, decision questions and source list.',
        'promise': 'The briefing does not guarantee a particular business outcome and does not replace specialist advice. Its purpose is to give leaders a concise, sourced view of the defined question.',
    },
    'b2b-charity-newsletter-production.html': {
        'scope': 'One newsletter edition or agreed recurring unit covering editorial plan, researched copy, production, approval workflow and schedule.',
        'promise': 'The service does not guarantee readership, engagement, leads or commercial results. The customer retains factual approval and publication authority.',
    },
    'explainer-and-thought-leadership-production.html': {
        'scope': 'One agreed article, report or script project covering research, structure, draft, citations where relevant, review and publication-ready copy.',
        'promise': 'The service does not guarantee reach, influence, leads or commercial results. The customer retains approval and publication authority, and the work does not invent expertise or evidence.',
    },
    'research-monitoring-horizon-scanning-subscription.html': {
        'scope': 'One defined monitoring service covering a topic, source set, cadence, alert threshold, sourced alerts, implications and change log.',
        'promise': 'Monitoring cannot guarantee that every external development will be captured or that an identified change will lead to a particular business outcome. Coverage is limited to the agreed source set and cadence.',
    },
    'church-and-parish-grant-funding-research.html': {
        'trust': 'Practical funding research only · parish and Church decisions remain with the competent authority · no funding guarantee.',
        'promise': 'We do not guarantee funding or a particular funder decision. The parish remains responsible for its project and applications, with ecclesiastical or professional decisions staying with the competent authority.',
        'replacements': (
            ('temporal project', 'practical project'), ('Temporal project', 'Practical project'),
        ),
    },
    'church-grant-application-development-support.html': {
        'scope': 'One grant-application support project covering application planning, evidence assembly, focused drafting and editing, timetable, review and submission-readiness checklist.',
        'trust': 'Practical application support only · the parish remains applicant and decision-maker · no funding guarantee.',
        'promise': 'We do not guarantee funding or a successful application. The parish remains the applicant, owns the evidence and approves and submits the final application.',
    },
    'church-building-funding-and-maintenance-roadmap.html': {
        'scope': 'One building and funding roadmap based on existing competent evidence, covering priorities, dependencies, funding routes, decision schedule and specialist referrals.',
        'trust': 'Practical planning support only · regulated property and Church decisions stay with the competent professionals and authorities.',
        'promise': 'The roadmap does not guarantee funding or a building outcome and does not replace architectural, surveying, engineering, legal or Church authority.',
        'replacements': (
            ('temporal works-and-funding', 'works-and-funding'), ('Temporal works-and-funding', 'Works-and-funding'),
            ('temporal works', 'works'), ('Temporal works', 'Works'),
            ('temporal programme', 'practical programme'), ('Temporal programme', 'Practical programme'),
        ),
    },
    'parish-operations-and-administration-improvement.html': {
        'hook': 'Improve parish administration through clearer processes, records, responsibilities and suitable digital tools.',
        'scope': 'One parish-administration improvement project covering operations review, priority process changes, records structure, meeting and administration routines, SOPs and handover.',
        'trust': 'Practical administration support only · pastoral, sacramental and ecclesiastical authority remain with the parish and Church.',
        'promise': 'The service does not guarantee time savings or organisational outcomes and does not replace parish, pastoral or ecclesiastical authority.',
        'replacements': (
            ('agreed temporal administration', 'agreed administrative work'),
            ('temporal parish administration', 'parish administration'),
            ('Temporal parish administration', 'Parish administration'),
        ),
    },
    'parish-digital-and-ai-governance-starter-service.html': {
        'scope': 'One parish digital and AI governance starter project covering tool and use review, practical data and AI rules, acceptable-use guidance, one SOP, briefing and escalation routes.',
        'trust': 'Practical digital-governance support only · diocesan, safeguarding, legal and specialist authority remain where they belong.',
        'promise': 'The service does not guarantee compliance or replace diocesan, legal, DPO, safeguarding or security advice where that is required.',
    },
    'parish-communications-service.html': {
        'scope': 'One agreed parish communications unit or recurring service covering content, notices, information structure, communications calendar and production workflow.',
        'trust': 'Practical communications support only · facts, voice and publication authority remain with the parish.',
        'promise': 'The service does not guarantee engagement or other communications outcomes. The parish retains factual, editorial and publication authority.',
        'replacements': (
            ('temporal communications', 'parish communications'), ('Temporal communications', 'Parish communications'),
        ),
    },
    'charity-ai-governance-pack-and-implementation.html': {
        'hook': 'Turn approved AI requirements into practical rules, roles and working procedures that fit charity accountability and day-to-day work.',
        'scope': 'One charity AI-governance implementation covering charity-adapted policy, SOPs, roles, briefing and implementation checklist.',
        'promise': 'The service does not guarantee compliance or organisational outcomes. Trustees and the charity retain their legal and governance responsibilities.',
        'replacements': (
            ('House AI-governance framework', 'AI governance framework'),
            ('House AI-governance kernel', 'AI governance framework'),
        ),
    },
    'charity-cyber-and-digital-governance-readiness-review.html': {
        'scope': 'One governance-level digital and cyber readiness review covering oversight, asset and control questions, priority actions, ownership and specialist referrals.',
        'promise': 'The review does not guarantee cyber security or compliance and is not a technical security audit or certification. Trustees and managers retain the decisions.',
    },
    'charity-governance-and-trustee-information-pack-review.html': {
        'scope': 'One trustee-information pack review covering decision clarity, evidence and risk critique, actionability and prioritised improvements.',
        'promise': 'The review does not guarantee better decisions or governance outcomes and does not replace trustee judgement, legal advice or regulator authority.',
    },
    'public-sector-decision-governance-review.html': {
        'scope': 'One defined public-sector decision route, covering current process, recorded authority, evidence standards, hand-offs and improvement recommendations.',
        'promise': 'The review does not determine legal powers or replace the body’s formal governance and legal authority. It does not guarantee an operational outcome.',
    },
    'committee-board-paper-quality-review.html': {
        'scope': 'One committee or board paper review covering decision framing, evidence, risks and actionability, and prioritised revisions.',
        'promise': 'The review does not guarantee approval or a particular decision. It does not replace legal, governance-officer or formal sign-off.',
    },
    'public-sector-sop-and-process-modernisation.html': {
        'scope': 'One defined administrative process covering current-state map, redesigned process, SOP, tool options, controls and implementation plan.',
        'promise': 'The service does not guarantee savings or productivity outcomes and does not override public-sector procurement, records, security or statutory controls.',
        'replacements': (
            ('bounded administrative process', 'defined administrative process'),
            ('focused administrative process', 'defined administrative process'),
            ('Bounded administrative process', 'Defined administrative process'),
            ('Focused administrative process', 'Defined administrative process'),
        ),
    },
    'consultation-and-evidence-synthesis-service.html': {
        'scope': 'One defined consultation or evidence synthesis covering coding method, themes, contrary evidence, limitations and source or data appendix.',
        'promise': 'The synthesis does not guarantee representativeness or a particular decision outcome. Conclusions are limited to the supplied evidence and agreed method.',
    },
}


def add_css(html):
    if 'assets/hoc-cx.css' in html:
        return html
    return html.replace('</head>', '  <link rel="stylesheet" href="assets/hoc-cx.css">\n</head>', 1)


def replace_class_inner(html, class_name, new_inner):
    pattern = re.compile(
        r'(<(?P<tag>\w+)\b[^>]*class="[^"]*\b' + re.escape(class_name) + r'\b[^"]*"[^>]*>)(.*?)(</(?P=tag)>)',
        re.I | re.S,
    )
    return pattern.sub(lambda m: m.group(1) + new_inner + m.group(4), html, count=1)


def replace_disclosure_answer(html, answer):
    pattern = re.compile(
        r'(<summary>What this service does not promise</summary>\s*<div\b[^>]*class="[^"]*\bhoc-accordion-panel\b[^"]*"[^>]*>)(.*?)(</div>\s*</details>)',
        re.I | re.S,
    )
    updated, count = pattern.subn(lambda m: m.group(1) + '<p>' + answer + '</p>' + m.group(3), html, count=1)
    if count != 1:
        raise SystemExit('CX FINISH FAIL: could not locate customer promise disclosure')
    return updated


def clean_description_metadata(html):
    def clean_tag(match):
        tag = match.group(0)
        if not re.search(r'\bname=["\']description["\']', tag, re.I):
            return tag

        def clean_content(content_match):
            value = content_match.group(2)
            for old, new in META_REPLACEMENTS:
                value = value.replace(old, new)
            return content_match.group(1) + value + content_match.group(3)

        return re.sub(r'(\bcontent=["\'])(.*?)(["\'])', clean_content, tag, count=1, flags=re.I | re.S)

    return re.sub(r'<meta\b[^>]*>', clean_tag, html, flags=re.I | re.S)


def finish_product(path):
    html = path.read_text(encoding='utf-8')
    html = html.replace(
        'You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.',
        'This service is complete in its own right. You do not need another service for this one to be worthwhile. If the work uncovers a separate problem worth solving, these are the most likely next steps.',
    )
    html = html.replace(
        'the customer, problem, information available and requested what you need this service',
        'the customer, problem, available information and requested scope are suitable for this service',
    )
    html = clean_description_metadata(html)
    html = add_css(html)
    path.write_text(html, encoding='utf-8')


def remediate_product(path):
    html = path.read_text(encoding='utf-8')
    for old, new in PRODUCT_NAME_REPLACEMENTS.get(path.name, ()):
        html = html.replace(old, new)
    spec = PRODUCT_REMEDIATION.get(path.name)
    if spec:
        for old, new in spec.get('replacements', ()):
            html = html.replace(old, new)
        if 'hook' in spec:
            html = replace_class_inner(html, 'product-hook', '<strong>' + spec['hook'] + '</strong>')
        if 'scope' in spec:
            html = replace_class_inner(html, 'product-scope-line', spec['scope'])
        if 'trust' in spec:
            html = replace_class_inner(html, 'product-trust-line', '<strong>' + spec['trust'] + '</strong>')
        if 'promise' in spec:
            html = replace_disclosure_answer(html, spec['promise'])
    path.write_text(html, encoding='utf-8')


def transform_catalogues():
    replacements = {
        'catalogue.html': (
            ('Fifty-three practical House of Carol services across operations, AI and digital work, commercial processes, learning, research, charities, public-sector organisations, churches and parishes.',
             'Practical House of Carol services across seven areas of work, organised around the problem you need to solve.'),
            ('<p class="eyebrow">53 services · seven areas</p>', '<p class="eyebrow">Seven practical service areas</p>'),
            ('<p class="service-note">Each service page explains what the work is for, what you receive and the boundaries of the service.</p>',
             '<p class="service-note">Each service page explains the work and its boundaries. If you are not sure which one fits, tell us the problem and we’ll identify the smallest sensible starting point.</p>'),
            ('Temporal parish work — funding, buildings, administration, governance, digital choices or communications — needs practical support.',
             'Parish work — funding, buildings, administration, governance, digital choices or communications — needs practical support.'),
        ),
        'catalogue-ai-digital.html': (
            ('<h3>Independent Document Review</h3>', '<h3>AI Output Assurance &amp; Red-Team Review</h3>'),
            ('<p class="service-for"><strong>When:</strong> an important proposal, board paper, report or submission needs independent challenge before it is relied on or released.</p>',
             '<p class="service-for"><strong>When:</strong> an important AI-assisted document or presentation needs an independent challenge of its facts, evidence, reasoning and boundaries before it is relied on or released.</p>'),
            ('Challenge one material document for factual support, source use, reasoning, omissions and decision risk before it is relied on or released.',
             'Challenge one material AI-assisted output for factual support, source use, reasoning, omissions and boundary failures before it is relied on or released.'),
        ),
        'catalogue-research.html': (
            ('source universe', 'set of sources'), ('Source universe', 'Set of sources'),
        ),
        'catalogue-church-parish.html': (
            ('Practical support for the temporal work of churches and parishes.', 'Practical support for the everyday operational work of churches and parishes.'),
            ('a defined temporal project', 'a defined practical project'),
            ('the temporal project need', 'the practical project need'),
            ('temporal works and funding priorities', 'building works and funding priorities'),
            ('a prioritised temporal works-and-funding roadmap without impersonating regulated property professionals.',
             'a prioritised works-and-funding roadmap while keeping regulated property judgement with the appropriate professionals.'),
            ('Improve temporal parish administration through clearer processes, records, responsibilities and suitable digital tools.',
             'Improve parish administration through clearer processes, records, responsibilities and suitable digital tools.'),
            ('reliable temporal communications production while retaining its own approval and Church authority boundaries.',
             'reliable parish communications while retaining its own approval and Church authority boundaries.'),
            ('Provide reliable temporal communications production while preserving parish approval and Church authority boundaries.',
             'Provide reliable parish communications while preserving parish approval and Church authority boundaries.'),
            ('Share the temporal problem, the relevant authority boundaries and what a useful result would look like.',
             'Share the operational problem, the relevant authority boundaries and what a useful result would look like.'),
        ),
        'catalogue-charity-public.html': (
            ('House AI-governance kernel', 'approved AI requirements'),
            ('House AI-governance framework', 'approved AI requirements'),
            ('bounded administrative process', 'defined administrative process'),
            ('focused administrative process', 'defined administrative process'),
            ('Bounded administrative process', 'Defined administrative process'),
            ('Focused administrative process', 'Defined administrative process'),
        ),
    }
    for name, pairs in replacements.items():
        path = ROOT / name
        html = path.read_text(encoding='utf-8')
        for old, new in pairs:
            html = html.replace(old, new)
        path.write_text(html, encoding='utf-8')


products = []
for path in ROOT.glob('*.html'):
    text = path.read_text(encoding='utf-8')
    if re.search(r'<body\b[^>]*class="[^"]*\bcanonical-product-page\b', text, re.I) and 'product-fee-text' in text:
        products.append(path)
if len(products) != 53:
    raise SystemExit(f'CX FINISH FAIL: expected 53 products, found {len(products)}')
for p in products:
    finish_product(p)
    remediate_product(p)
transform_catalogues()
for name in ['worked-example-ai-workflow.html', 'worked-example-process-handover.html', 'worked-example-trade-account-customer-journey.html', 'worked-examples.html']:
    p = ROOT / name
    p.write_text(add_css(p.read_text(encoding='utf-8')), encoding='utf-8')
print('PASS: finalised customer-experience presentation and approved brand/editorial remediation while preserving commercial scope')
