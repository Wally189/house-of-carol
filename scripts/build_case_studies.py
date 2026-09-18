from pathlib import Path
from html import unescape, escape
import re

ROOT = Path(__file__).resolve().parents[1]

# Current 54 DEVELOP routes. The Business Plan remains authoritative for the
# portfolio; this build list mirrors the current website contract and is checked
# by product_page_standardisation_check.py.
PRODUCTS = [
    'ai-data-use-rules-sprint.html',
    'ai-policy-and-sop-implementation-service.html',
    'responsible-ai-workplace-training.html',
    'role-based-ai-skills-workshop.html',
    'ai-leadership-and-management-workshop.html',
    'ai-workflow-opportunity-review.html',
    'ai-workflow-implementation-sprint.html',
    'ai-tool-and-account-governance-review.html',
    'ai-vendor-tool-selection-review.html',
    'independent-document-review.html',
    'ai-operating-model-and-governance-blueprint.html',
    'ai-adoption-support-retainer.html',
    'no-code-ai-automation-implementation.html',
    'business-knowledge-base-and-ai-retrieval-setup.html',
    'process-design-sprint.html',
    'shared-drive-cleanup.html',
    'management-information-and-kpi-setup.html',
    'managed-business-administration.html',
    'customer-journey-and-service-operations-review.html',
    'customer-support-knowledge-base-build.html',
    'business-continuity-and-operational-readiness-pack.html',
    'decision-rights-and-governance-review.html',
    'complaints-and-redress-process-design.html',
    'evidence-and-marketing-claim-substantiation-review.html',
    'tender-review.html',
    'tender-readiness-and-bid-evidence-library.html',
    'public-procurement-opportunity-monitoring.html',
    'invoice-to-cash-process-setup.html',
    'cash-flow-and-financial-operations-setup.html',
    'supplier-and-purchasing-process-setup.html',
    'bespoke-organisational-training-design.html',
    'assessment-and-competency-framework-design.html',
    'internal-academy-learning-pathway-design.html',
    'microlearning-and-scenario-assessment-packs.html',
    'research-briefing.html',
    'training-quality-review.html',
    'church-and-parish-grant-funding-research.html',
    'church-grant-application-development-support.html',
    'church-building-funding-and-maintenance-roadmap.html',
    'parish-operations-and-administration-improvement.html',
    'parish-digital-and-ai-governance-starter-service.html',
    'parish-communications-service.html',
    'charity-ai-governance-pack-and-implementation.html',
    'charity-cyber-and-digital-governance-readiness-review.html',
    'charity-governance-and-trustee-information-pack-review.html',
    'public-sector-decision-governance-review.html',
    'committee-board-paper-quality-review.html',
    'public-sector-sop-and-process-modernisation.html',
    'consultation-and-evidence-synthesis-service.html',
    'evidence-based-executive-briefing-service.html',
    'b2b-charity-newsletter-production.html',
    'explainer-and-thought-leadership-production.html',
    'research-monitoring-horizon-scanning-subscription.html',
    'website-completion-sprint.html',
]

# Evidence-honest product adjacency. Every route has a bounded set of no more
# than three currently activatable DEVELOP routes. The condition is customer-led:
# a separate need must actually be present before another service is relevant.
RELATIONS = {
    'ai-data-use-rules-sprint.html': [
        ('ai-policy-and-sop-implementation-service.html', 'the data-use questions reveal a wider gap in organisational AI rules, responsibilities or procedures', 'turn those governance requirements into practical policy and SOPs'),
        ('responsible-ai-workplace-training.html', 'the rule is clear but staff still need practice applying responsible judgement in ordinary work', 'build a practical responsible-AI workplace baseline'),
    ],
    'ai-policy-and-sop-implementation-service.html': [
        ('ai-data-use-rules-sprint.html', 'managers still need a more specific practical rule for deciding what information may be used with particular AI tools or account types', 'turn that recurring question into a clear day-to-day decision rule'),
        ('ai-operating-model-and-governance-blueprint.html', 'the work shows that AI adoption is fragmented across roles, tools, use cases and governance routines rather than being only a policy problem', 'design the wider operating model'),
        ('responsible-ai-workplace-training.html', 'the policy and SOPs are clear but staff need practice applying responsible judgement', 'build a practical shared workplace baseline'),
    ],
    'responsible-ai-workplace-training.html': [
        ('role-based-ai-skills-workshop.html', 'the shared baseline is in place but one team needs deeper practice on the recurring AI-enabled workflows of its specific role', 'turn general judgement into role-based working capability'),
        ('ai-data-use-rules-sprint.html', 'the scenarios expose a recurring unresolved question about what information may be used with particular AI tools or accounts', 'create a practical organisation-specific decision rule'),
        ('ai-policy-and-sop-implementation-service.html', 'staff uncertainty is being caused by missing organisational rules, responsibilities or procedures rather than a training gap', 'put the governance foundation in place'),
    ],
    'role-based-ai-skills-workshop.html': [
        ('ai-workflow-opportunity-review.html', 'the team can apply AI well but the organisation still does not know which wider workflows are worth testing', 'compare recurring workflows and decide where AI is appropriate, where something else should be fixed first and where not to proceed'),
        ('responsible-ai-workplace-training.html', 'the diagnostic shows that the group does not yet share a basic responsible-use foundation', 'establish that baseline before deeper role-specific practice'),
        ('ai-data-use-rules-sprint.html', 'progress is being blocked by recurring uncertainty about which information may be used with which AI tools or accounts', 'create a practical decision rule first'),
    ],
    'ai-leadership-and-management-workshop.html': [
        ('ai-workflow-opportunity-review.html', 'leaders need a deeper evidence-based comparison of several recurring workflows before choosing an AI test', 'turn the candidate workflows into explicit progress, fix-first, non-AI, hold or do-not-progress decisions'),
        ('ai-operating-model-and-governance-blueprint.html', 'the leadership discussion shows that AI adoption is fragmented across roles, tools and governance routines', 'design a proportionate operating model for the wider organisation'),
        ('ai-policy-and-sop-implementation-service.html', 'the decisions are made but the organisation now needs practical policies, responsibilities and procedures to implement them', 'convert governance choices into day-to-day operating rules'),
    ],
    'ai-workflow-opportunity-review.html': [
        ('ai-workflow-implementation-sprint.html', 'one low- or moderate-consequence use case is validated, bounded and ready to become a tested human-operated workflow', 'turn that use case into a repeatable working method'),
        ('process-design-sprint.html', 'the review shows that the underlying workflow is the real problem and should be fixed before adding AI', 'redesign and document the process first'),
        ('ai-vendor-tool-selection-review.html', 'the use case is clear but the organisation still needs to compare candidate AI tools against defined requirements', 'make an evidence-based tool choice with visible trade-offs'),
    ],
    'ai-workflow-implementation-sprint.html': [
        ('independent-document-review.html', 'the implemented workflow will produce material AI-assisted outputs that need structured adversarial checking before use', 'strengthen factual, evidential and reasoning assurance'),
        ('ai-adoption-support-retainer.html', 'questions, new use cases or bounded updates become an ongoing need rather than a one-off implementation issue', 'provide a controlled recurring support route'),
    ],
    'ai-tool-and-account-governance-review.html': [
        ('ai-data-use-rules-sprint.html', 'the estate review exposes recurring uncertainty about what information may be used with particular tools or account types', 'create a practical data-use decision rule'),
        ('ai-vendor-tool-selection-review.html', 'the organisation now needs to rationalise or choose between competing AI tools against defined requirements', 'compare options on a consistent evidence basis'),
        ('ai-policy-and-sop-implementation-service.html', 'the control gaps require organisation-wide rules, responsibilities or repeatable procedures', 'turn the governance decisions into practical policy and SOPs'),
    ],
    'ai-vendor-tool-selection-review.html': [
        ('ai-workflow-opportunity-review.html', 'the organisation has not yet established which workflows actually justify an AI tool decision', 'identify the worthwhile use cases before selecting technology'),
        ('ai-tool-and-account-governance-review.html', 'the decision exposes wider ownership, account or permission questions across the existing tool estate', 'clarify governance of the tools and accounts already in use'),
        ('ai-workflow-implementation-sprint.html', 'a selected tool and validated low- or moderate-consequence use case are ready for bounded implementation', 'turn the chosen use case into a tested human-operated workflow'),
    ],
    'independent-document-review.html': [
        ('evidence-and-marketing-claim-substantiation-review.html', 'the material includes public-facing factual or performance claims that need a dedicated evidence-to-claim check', 'challenge those claims against the available substantiation before release'),
        ('research-briefing.html', 'the review exposes an evidence gap that requires a defined research question to be answered before the document can be settled', 'produce a sourced briefing with uncertainty and competing evidence visible'),
    ],
    'ai-operating-model-and-governance-blueprint.html': [
        ('ai-policy-and-sop-implementation-service.html', 'the operating model decisions now need to be translated into practical policy, responsibilities and procedures', 'implement the agreed governance in day-to-day work'),
        ('ai-leadership-and-management-workshop.html', 'leaders first need to make or align the core opportunity, risk and prioritisation decisions', 'create the management decisions that the operating model should reflect'),
        ('ai-adoption-support-retainer.html', 'the model is in place but governance questions and new use cases become an ongoing bounded support need', 'provide controlled recurring support'),
    ],
    'ai-adoption-support-retainer.html': [
        ('role-based-ai-skills-workshop.html', 'recurring support questions show that one team needs deeper capability in its own workflows', 'build role-specific AI-assisted working practice'),
        ('independent-document-review.html', 'a material AI-assisted output needs a separate structured review before use or release', 'apply adversarial evidence and reasoning checks'),
        ('ai-policy-and-sop-implementation-service.html', 'repeated questions show that the underlying policy or operating procedure needs a durable update', 'fix the governance source rather than treating the same issue as recurring support'),
    ],
    'no-code-ai-automation-implementation.html': [
        ('process-design-sprint.html', 'the process is unstable, exception-heavy or unclear enough that automating it would simply hard-code the mess', 'redesign the process before implementing automation'),
        ('ai-workflow-opportunity-review.html', 'the organisation is not yet sure whether AI or automation is the right intervention for the recurring work', 'compare the workflow options and decide what is worth testing'),
    ],
    'business-knowledge-base-and-ai-retrieval-setup.html': [
        ('shared-drive-cleanup.html', 'the main obstacle is duplicate, stale or poorly controlled source material rather than retrieval configuration', 'clean up the information estate and clarify the source of truth first'),
        ('customer-support-knowledge-base-build.html', 'the bounded knowledge domain is specifically a customer-support area that needs approved answers and escalation ownership', 'turn the source material into a maintainable support knowledge base'),
        ('ai-adoption-support-retainer.html', 'new retrieval questions and bounded updates become an ongoing need after the baseline is accepted', 'provide controlled recurring support rather than an open-ended build'),
    ],
    'process-design-sprint.html': [
        ('customer-journey-and-service-operations-review.html', 'the process problem is actually one part of a wider end-to-end customer journey', 'map the whole journey before deciding what to change next'),
        ('shared-drive-cleanup.html', 'the redesigned process depends on a document area where duplicates, stale files or unclear sources of truth keep breaking the hand-offs', 'create a simpler controlled information structure'),
        ('management-information-and-kpi-setup.html', 'the new process needs a small set of decision-useful measures and a practical reporting rhythm', 'build management information around the decisions the process owner needs to make'),
    ],
    'shared-drive-cleanup.html': [
        ('business-knowledge-base-and-ai-retrieval-setup.html', 'the cleaned source structure is stable and the next problem is reliable retrieval across a bounded knowledge domain', 'add a governed retrieval layer on top of the controlled sources'),
        ('process-design-sprint.html', 'the file disorder is being recreated by an unclear recurring process, ownership gap or weak hand-off', 'fix the process that produces and maintains the records'),
        ('business-continuity-and-operational-readiness-pack.html', 'the review exposes key-person, dependency or recovery risks around essential information', 'build a proportionate continuity baseline around the critical service'),
    ],
    'management-information-and-kpi-setup.html': [
        ('process-design-sprint.html', 'the measures expose a recurring process that lacks clear ownership, hand-offs or control points', 'redesign the underlying process rather than only reporting on it'),
        ('cash-flow-and-financial-operations-setup.html', 'the management-information gap is specifically about liquidity, cash timing and financial operating routines', 'create a practical cash-management baseline'),
        ('evidence-based-executive-briefing-service.html', 'leaders have reliable measures but need concise current intelligence and implications around a defined subject', 'turn the wider evidence into a sourced executive briefing'),
    ],
    'managed-business-administration.html': [
        ('process-design-sprint.html', 'the recurring administration is repeatedly failing because the underlying process or hand-offs are unclear', 'redesign the process before paying for somebody to keep rescuing it'),
        ('shared-drive-cleanup.html', 'routine administration is being slowed by duplicate, stale or poorly controlled documents and records', 'simplify the information estate before recurring maintenance continues'),
        ('management-information-and-kpi-setup.html', 'the real need is to define management measures or reporting rather than maintain an existing tracker or register', 'design the management-information layer as a separate piece of work'),
    ],
    'customer-journey-and-service-operations-review.html': [
        ('process-design-sprint.html', 'the journey review identifies one recurring operational process as the specific source of friction', 'redesign that bounded process and create a practical SOP'),
        ('customer-support-knowledge-base-build.html', 'customers and staff are being slowed by repeated questions or inconsistent support answers', 'build a structured support knowledge base with clear escalation'),
        ('website-completion-sprint.html', 'the journey problem is concentrated in an existing materially built website that is unfinished, inconsistent or technically unverified', 'finish and QA the existing site without an unnecessary rebuild'),
    ],
    'customer-support-knowledge-base-build.html': [
        ('customer-journey-and-service-operations-review.html', 'the support questions are symptoms of a wider fragmented customer journey rather than only a knowledge problem', 'map the end-to-end experience and the operational hand-offs behind it'),
        ('business-knowledge-base-and-ai-retrieval-setup.html', 'the approved support knowledge now needs governed retrieval across a bounded repository or domain', 'create the source structure and retrieval layer'),
        ('shared-drive-cleanup.html', 'the support team cannot maintain reliable answers because the underlying source estate is duplicated or unclear', 'simplify the document structure and source-of-truth rules'),
    ],
    'business-continuity-and-operational-readiness-pack.html': [
        ('shared-drive-cleanup.html', 'critical information is difficult to locate, duplicated or dependent on one person knowing the right file', 'strengthen the information baseline that continuity depends on'),
        ('decision-rights-and-governance-review.html', 'activation, escalation or recovery decisions are slowed by unclear authority', 'clarify who decides what and how matters escalate'),
        ('charity-cyber-and-digital-governance-readiness-review.html', 'a charity context exposes governance-level digital or cyber dependencies that need separate trustee oversight', 'turn those digital risks into prioritised governance actions and specialist referrals'),
    ],
    'decision-rights-and-governance-review.html': [
        ('process-design-sprint.html', 'the authority map reveals a recurring operational process whose hand-offs and responsibilities still need redesign', 'turn the decision model into a practical working process'),
        ('committee-board-paper-quality-review.html', 'the decision route is clear but papers still fail to frame the decision, evidence or risk effectively', 'improve the quality and actionability of the decision material'),
        ('business-continuity-and-operational-readiness-pack.html', 'the governance review exposes unclear activation, recovery or dependency decisions around essential work', 'create a proportionate continuity baseline'),
    ],
    'complaints-and-redress-process-design.html': [
        ('customer-journey-and-service-operations-review.html', 'complaints reveal repeated friction across the wider customer journey rather than a problem confined to complaint handling', 'map the end-to-end experience and prioritise the operational causes'),
        ('customer-support-knowledge-base-build.html', 'inconsistent answers or unclear support information are contributing to avoidable complaints', 'create approved support content and escalation ownership'),
        ('decision-rights-and-governance-review.html', 'investigation, remedy or escalation decisions remain slow because authority is unclear', 'clarify decision rights and escalation routes'),
    ],
    'evidence-and-marketing-claim-substantiation-review.html': [
        ('independent-document-review.html', 'the wider document also needs factual, evidential or reasoning challenge beyond the individual claims', 'apply a structured adversarial review to the complete output'),
        ('explainer-and-thought-leadership-production.html', 'the evidence is sound but the organisation needs to turn it into clear publication-ready explanation grounded in genuine expertise', 'research and produce accessible evidence-based content'),
        ('research-briefing.html', 'the claim review exposes a defined evidence gap that must be researched before a claim can be settled', 'answer the underlying question with sourced evidence and uncertainty visible'),
    ],
    'tender-review.html': [
        ('tender-readiness-and-bid-evidence-library.html', 'the same evidence hunt repeats across bids and the organisation needs a reusable source base before the next opportunity', 'create a maintained tender evidence library and capability structure'),
        ('research-briefing.html', 'a material bid point depends on a defined evidence question that the supplied tender pack does not answer', 'produce a bounded sourced briefing for the bid owner to use appropriately'),
        ('public-procurement-opportunity-monitoring.html', 'the organisation is ready to bid but relevant public opportunities are still being discovered too late', 'create a defined monitoring route around the agreed opportunity profile'),
    ],
    'tender-readiness-and-bid-evidence-library.html': [
        ('tender-review.html', 'a specific substantially complete tender now needs an independent structured challenge before submission', 'review the bid against the supplied requirements and evaluation criteria'),
        ('public-procurement-opportunity-monitoring.html', 'the evidence base is ready but suitable public opportunities are still being found inconsistently', 'monitor a defined opportunity profile and provide filtered alerts'),
        ('research-briefing.html', 'a recurring evidence theme in the library needs a dedicated sourced synthesis rather than repeated ad hoc research', 'create a reusable evidence briefing around the defined question'),
    ],
    'public-procurement-opportunity-monitoring.html': [
        ('tender-review.html', 'a monitored opportunity becomes a live substantially complete bid that needs structured challenge before submission', 'review the tender against its actual requirements and evaluation criteria'),
        ('tender-readiness-and-bid-evidence-library.html', 'the organisation repeatedly qualifies for opportunities but scrambles to assemble the same evidence each time', 'build a reusable evidence base for future bids'),
        ('research-briefing.html', 'a shortlisted opportunity raises a defined evidence question that needs a concise sourced answer', 'produce a decision-useful research briefing'),
    ],
    'invoice-to-cash-process-setup.html': [
        ('cash-flow-and-financial-operations-setup.html', 'the process review shows that the larger problem is cash visibility, timing and operating discipline rather than only billing and collection hand-offs', 'create a wider practical cash-management baseline'),
        ('management-information-and-kpi-setup.html', 'management needs decision-useful measures to see invoice-to-cash performance and exceptions clearly', 'define a small reporting structure tied to the decisions managers make'),
        ('supplier-and-purchasing-process-setup.html', 'the finance-operations review also exposes a separate ad hoc purchasing and supplier-control problem', 'create a proportionate purchasing process with clearer approvals and records'),
    ],
    'cash-flow-and-financial-operations-setup.html': [
        ('management-information-and-kpi-setup.html', 'the cash routine is in place but management still lacks a small set of decision-useful measures and reporting ownership', 'build a practical management-information layer'),
        ('invoice-to-cash-process-setup.html', 'delayed cash is being driven by fragmented billing, reminders, payment recording or reconciliation hand-offs', 'design the end-to-end invoice-to-cash process'),
        ('supplier-and-purchasing-process-setup.html', 'cash pressure is being worsened by ad hoc purchasing, unclear approvals or weak supplier decision records', 'create a proportionate purchasing process'),
    ],
    'supplier-and-purchasing-process-setup.html': [
        ('process-design-sprint.html', 'one recurring purchasing workflow remains dependent on workarounds, unclear hand-offs or manager rescue', 'redesign that bounded process and document the operating method'),
        ('management-information-and-kpi-setup.html', 'management lacks useful measures for purchasing decisions, exceptions or supplier performance', 'define a small decision-linked reporting structure'),
    ],
    'bespoke-organisational-training-design.html': [
        ('assessment-and-competency-framework-design.html', 'the learning design now needs a clearer model of what competent performance looks like and how it should be evidenced', 'create proportionate competency and assessment criteria'),
        ('internal-academy-learning-pathway-design.html', 'the need spans a coherent capability domain rather than one standalone learning intervention', 'design a structured internal pathway from foundation to applied capability'),
        ('training-quality-review.html', 'an existing programme should be challenged before it is rebuilt or expanded', 'review its design, assessment validity and likely transfer into performance'),
    ],
    'assessment-and-competency-framework-design.html': [
        ('bespoke-organisational-training-design.html', 'the competency model is clear but the organisation now needs learning designed around the required performance', 'build a programme with practice and assessment aligned to the capability'),
        ('training-quality-review.html', 'the organisation already has training and assessment material but needs an evidence-based review of whether it measures the intended capability', 'challenge the design and assessment approach'),
        ('microlearning-and-scenario-assessment-packs.html', 'a bounded part of the framework would benefit from short scenario-based practice and judgement checks', 'create concise learning and assessment materials for that topic'),
    ],
    'internal-academy-learning-pathway-design.html': [
        ('bespoke-organisational-training-design.html', 'one part of the pathway needs a bespoke learning intervention built around a specific performance requirement', 'design that learning unit with practice and assessment'),
        ('microlearning-and-scenario-assessment-packs.html', 'the pathway needs short practical learning components for defined decisions or behaviours', 'create concise scenario-based learning packs'),
        ('training-quality-review.html', 'existing academy material should be reviewed before being retained inside the new pathway', 'test its design, assessment validity and transfer logic'),
    ],
    'microlearning-and-scenario-assessment-packs.html': [
        ('bespoke-organisational-training-design.html', 'the topic requires a fuller learning intervention rather than a short bounded learning pack', 'design the wider programme around the actual performance requirement'),
        ('assessment-and-competency-framework-design.html', 'the scenarios expose a broader need to define and assess the underlying capability consistently', 'create a proportionate competency and assessment framework'),
        ('training-quality-review.html', 'existing short-form learning needs an evidence-based challenge before more content is produced', 'review whether the design and assessment are likely to achieve the intended outcome'),
    ],
    'research-briefing.html': [
        ('evidence-based-executive-briefing-service.html', 'the decision-maker needs continuing current intelligence around a defined subject rather than one research question', 'turn the information need into concise sourced executive briefings'),
        ('research-monitoring-horizon-scanning-subscription.html', 'the issue changes over time and the real need is to detect meaningful developments in a defined source universe', 'create a bounded monitoring and change-detection service'),
        ('evidence-and-marketing-claim-substantiation-review.html', 'the research will be used to support public factual or performance claims that need explicit substantiation checking', 'challenge the claims against the available evidence before release'),
    ],
    'training-quality-review.html': [
        ('bespoke-organisational-training-design.html', 'the review shows that the intervention needs redesign around the real performance requirement', 'create a stronger learning design with practice and assessment built in'),
        ('assessment-and-competency-framework-design.html', 'the main weakness is that expected competence and evidence standards are unclear', 'define the competency and assessment model'),
        ('internal-academy-learning-pathway-design.html', 'the review reveals fragmentation across multiple learning interventions rather than a single-course problem', 'design a coherent capability pathway'),
    ],
    'church-and-parish-grant-funding-research.html': [
        ('church-grant-application-development-support.html', 'a credible funding route is identified and the parish now needs help organising truthful evidence, narrative, budget and submission readiness', 'develop the application materials while the parish remains the applicant and decision-maker'),
        ('church-building-funding-and-maintenance-roadmap.html', 'the funding question cannot be separated from a wider set of building priorities, dependencies and evidence needs', 'turn the available building evidence into a prioritised works-and-funding roadmap'),
    ],
    'church-grant-application-development-support.html': [
        ('church-and-parish-grant-funding-research.html', 'the parish has a project but does not yet know which credible funders or programmes match it', 'identify and prioritise the plausible funding routes first'),
        ('church-building-funding-and-maintenance-roadmap.html', 'the application is only one part of a wider programme of building needs and funding decisions', 'create a prioritised temporal works-and-funding roadmap'),
    ],
    'church-building-funding-and-maintenance-roadmap.html': [
        ('church-and-parish-grant-funding-research.html', 'the roadmap identifies a defined project that now needs a current prioritised view of credible funders', 'research the matched funding routes and evidence requirements'),
        ('church-grant-application-development-support.html', 'a suitable funding route is identified and the parish is ready to organise the evidence and application', 'develop the application toward submission readiness'),
        ('parish-operations-and-administration-improvement.html', 'the roadmap exposes recurring temporal administration, record or ownership problems that make the programme harder to manage', 'improve the underlying parish operating methods'),
    ],
    'parish-operations-and-administration-improvement.html': [
        ('process-design-sprint.html', 'one recurring temporal administration process needs deeper redesign, clearer hand-offs and a practical SOP', 'sort out that bounded process in detail'),
        ('parish-digital-and-ai-governance-starter-service.html', 'the administration review exposes unclear digital or AI use, data-handling or volunteer rules', 'create a proportionate parish digital and AI governance baseline'),
        ('parish-communications-service.html', 'the main operational pressure is recurring production and approval of parish notices, newsletters or web content', 'create a controlled communications production workflow'),
    ],
    'parish-digital-and-ai-governance-starter-service.html': [
        ('ai-data-use-rules-sprint.html', 'the parish still needs a more specific practical rule for deciding what information may be used with particular AI tools or accounts', 'create a clear day-to-day data-use rule within the agreed authority boundary'),
        ('ai-policy-and-sop-implementation-service.html', 'the issue has widened into organisation-level AI rules, responsibilities and procedures beyond the parish starter scope', 'implement a fuller practical policy and SOP framework'),
        ('responsible-ai-workplace-training.html', 'approved rules are in place but staff or volunteers need practical training in responsible everyday AI use', 'build a shared responsible-use baseline'),
    ],
    'parish-communications-service.html': [
        ('b2b-charity-newsletter-production.html', 'the recurring need is a structured newsletter or stakeholder-update production service with a clear approval workflow', 'use a dedicated editorial production model for repeat editions'),
        ('parish-operations-and-administration-improvement.html', 'communications problems are symptoms of wider temporal administration, records or responsibility gaps', 'improve the underlying parish operating system'),
        ('explainer-and-thought-leadership-production.html', 'the parish needs a separate evidence-grounded explainer or longer-form piece rather than routine notices and updates', 'research and produce a clear publication-ready explanation'),
    ],
    'charity-ai-governance-pack-and-implementation.html': [
        ('ai-policy-and-sop-implementation-service.html', 'the charity need extends beyond the charity-specific pack into a broader organisation-wide AI policy and SOP implementation', 'apply the fuller governance implementation service'),
        ('responsible-ai-workplace-training.html', 'trustee and management rules are in place but staff or volunteers need practical responsible-use training', 'build a shared workplace baseline'),
        ('charity-cyber-and-digital-governance-readiness-review.html', 'the work exposes wider trustee-level digital, cyber or information-risk uncertainty beyond AI governance', 'turn those risks into prioritised governance actions and specialist referrals'),
    ],
    'charity-cyber-and-digital-governance-readiness-review.html': [
        ('business-continuity-and-operational-readiness-pack.html', 'the review exposes material dependencies, fallback or recovery questions around essential services', 'create a proportionate continuity baseline'),
        ('charity-ai-governance-pack-and-implementation.html', 'AI use is the specific governance gap that now needs practical trustee visibility, staff rules and implementation', 'put the charity AI governance baseline in place'),
        ('decision-rights-and-governance-review.html', 'the review shows that digital-risk decisions or escalation routes are unclear', 'clarify who decides what and how material issues escalate'),
    ],
    'charity-governance-and-trustee-information-pack-review.html': [
        ('committee-board-paper-quality-review.html', 'one or more specific papers need a deeper structured review of decision framing, evidence, risk and actionability', 'apply the dedicated paper-quality review'),
        ('decision-rights-and-governance-review.html', 'the pack problems reflect unclear reserved and delegated decisions or weak escalation routes', 'clarify the organisation’s decision rights and governance routines'),
        ('research-briefing.html', 'trustees need a concise sourced answer to a defined evidence question before a decision can be settled', 'produce a bounded research briefing with uncertainty visible'),
    ],
    'public-sector-decision-governance-review.html': [
        ('decision-rights-and-governance-review.html', 'the operational issue can be addressed as a general decision-rights problem without requiring public-sector statutory interpretation', 'clarify decision ownership, escalation and governance routines'),
        ('committee-board-paper-quality-review.html', 'the route and authority are clear but decision papers still need stronger framing, evidence and actionability', 'improve the quality of the material supporting the decision'),
        ('public-sector-sop-and-process-modernisation.html', 'the governance review identifies a bounded routine administrative process whose steps and hand-offs should be modernised', 'redesign the process and produce a practical SOP and implementation plan'),
    ],
    'committee-board-paper-quality-review.html': [
        ('decision-rights-and-governance-review.html', 'the paper problem reveals wider uncertainty about who owns the decision, what is reserved or how matters escalate', 'clarify the governance model around the decision'),
        ('research-briefing.html', 'the draft cannot be settled because a defined evidence question remains unanswered', 'produce a sourced briefing for the decision owner'),
        ('consultation-and-evidence-synthesis-service.html', 'the paper depends on a large consultation or evidence set that needs transparent coding, themes, contrary evidence and limitations', 'turn that material into a structured synthesis before the paper is finalised'),
    ],
    'public-sector-sop-and-process-modernisation.html': [
        ('process-design-sprint.html', 'the problem can be treated as one ordinary recurring process without a material public-sector authority or records dimension', 'use the general bounded process-design service'),
        ('management-information-and-kpi-setup.html', 'the modernised process needs a small set of decision-useful measures and reporting ownership', 'create a practical management-information layer'),
        ('public-sector-decision-governance-review.html', 'the process is constrained by unclear delegations, decision routes or governance ownership', 'review the operational governance before redesign goes further'),
    ],
    'consultation-and-evidence-synthesis-service.html': [
        ('research-briefing.html', 'the synthesis exposes a defined evidence question that requires additional source research beyond the consultation material', 'answer that question with a bounded sourced briefing'),
        ('evidence-based-executive-briefing-service.html', 'decision-makers need the synthesis converted into a concise current briefing with implications and decision questions', 'create an executive-facing evidence brief'),
        ('committee-board-paper-quality-review.html', 'the synthesis is complete but the final decision paper needs a separate structured challenge', 'improve the framing, evidence, risk visibility and actionability of the paper'),
    ],
    'evidence-based-executive-briefing-service.html': [
        ('research-monitoring-horizon-scanning-subscription.html', 'the subject changes often enough that the organisation needs continuing monitoring rather than one briefing', 'track a defined source universe and surface meaningful developments'),
        ('research-briefing.html', 'the executive brief exposes one decision question that needs deeper bounded research', 'produce a fuller sourced synthesis around that question'),
        ('explainer-and-thought-leadership-production.html', 'the evidence is settled and now needs to be communicated to a wider audience in an accessible publication-ready form', 'turn the material into a clear explainer or thought-leadership piece'),
    ],
    'b2b-charity-newsletter-production.html': [
        ('explainer-and-thought-leadership-production.html', 'one newsletter topic needs a deeper evidence-grounded article, report or script rather than routine edition copy', 'produce the longer-form piece around the customer’s genuine expertise'),
        ('evidence-and-marketing-claim-substantiation-review.html', 'an edition contains material factual or performance claims that need dedicated substantiation checking', 'challenge those claims before publication'),
        ('research-monitoring-horizon-scanning-subscription.html', 'the editorial plan depends on regularly detecting meaningful developments in a defined source universe', 'create a bounded research-monitoring feed for the publication process'),
    ],
    'explainer-and-thought-leadership-production.html': [
        ('evidence-and-marketing-claim-substantiation-review.html', 'the finished content contains material factual or performance claims whose evidential support needs a separate challenge', 'review the claims and required qualifications before release'),
        ('research-briefing.html', 'the subject contains a defined evidence question that needs deeper research before drafting can responsibly continue', 'produce the source synthesis first'),
        ('b2b-charity-newsletter-production.html', 'the requirement becomes a recurring approved newsletter or stakeholder-update production need rather than one standalone piece', 'move into a repeatable editorial production service'),
    ],
    'research-monitoring-horizon-scanning-subscription.html': [
        ('evidence-based-executive-briefing-service.html', 'the monitoring feed needs to be converted into concise recurring briefings for executives or boards', 'turn meaningful changes into sourced implications and decision questions'),
        ('research-briefing.html', 'a detected development raises one defined question that requires deeper bounded research', 'produce a focused evidence briefing'),
        ('evidence-and-marketing-claim-substantiation-review.html', 'monitoring findings will support public factual or performance claims that need explicit substantiation checking', 'review those claims before publication'),
    ],
    'website-completion-sprint.html': [
        ('customer-journey-and-service-operations-review.html', 'the unfinished site is only one visible part of a wider fragmented customer journey and service-operation problem', 'map the end-to-end journey before making further changes'),
        ('evidence-and-marketing-claim-substantiation-review.html', 'the site contains material factual or performance claims whose support or qualifications are unclear', 'challenge the claims against the available evidence before release'),
        ('customer-support-knowledge-base-build.html', 'the site work exposes repeated customer questions or inconsistent support information that need a maintainable answer base', 'build a structured support knowledge base with escalation ownership'),
    ],
}

STANDALONE_EXAMPLES = {
    'ai-workflow-opportunity-review.html': ('worked-example-ai-workflow.html', 'See the AI workflow example →'),
    'ai-workflow-implementation-sprint.html': ('worked-example-ai-workflow.html', 'See the AI workflow example →'),
    'process-design-sprint.html': ('worked-example-process-handover.html', 'See the process example →'),
    'managed-business-administration.html': ('worked-example-process-handover.html', 'See the process example →'),
    'customer-journey-and-service-operations-review.html': ('worked-example-trade-account-customer-journey.html', 'See the customer-journey example →'),
}

IDENTITY_BANNER = '<section class="identity-banner" aria-label="House of Carol"><img src="assets/house-of-carol-identity.webp" alt="House of Carol — People, Ideas, Solutions, Real Progress. Intelligence for a kinder, more capable world." width="1536" height="1152"></section>'


def fail(message):
    raise SystemExit('BUILD FAIL: ' + message)


def plain(fragment):
    fragment = re.sub(r'<[^>]+>', ' ', fragment or '')
    return re.sub(r'\s+', ' ', unescape(fragment)).strip()


def first_h1(source):
    match = re.search(r'<h1\b[^>]*>(.*?)</h1>', source, re.I | re.S)
    return plain(match.group(1)) if match else ''


def first_class_paragraph(source, class_name):
    match = re.search(rf'<p\b[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>(.*?)</p>', source, re.I | re.S)
    return plain(match.group(1)) if match else ''


def section_bounds_for_heading(source, heading):
    pos = source.find(f'<h2>{heading}</h2>')
    if pos < 0:
        fail(f'missing heading {heading}')
    start = source.rfind('<section', 0, pos)
    end = source.find('</section>', pos)
    if start < 0 or end < 0:
        fail(f'cannot locate section for {heading}')
    return start, end + len('</section>')


def first_body_paragraph(source, heading):
    start, end = section_bounds_for_heading(source, heading)
    block = source[start:end]
    paragraphs = [plain(item) for item in re.findall(r'<p\b[^>]*>(.*?)</p>', block, re.I | re.S)]
    paragraphs = [item for item in paragraphs if item]
    return paragraphs[0] if paragraphs else ''


def deliverable_names(source):
    start, end = section_bounds_for_heading(source, 'What you will receive')
    block = source[start:end]
    names = [plain(item) for item in re.findall(r'<h3\b[^>]*>(.*?)</h3>', block, re.I | re.S)]
    return [name for name in names if name][:7]


def sentence_list(items):
    if not items:
        return 'the bounded deliverables described on this page'
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f'{items[0]} and {items[1]}'
    return ', '.join(items[:-1]) + ', and ' + items[-1]


def build_worked_example(route, source, title):
    problem = first_class_paragraph(source, 'intro') or first_class_paragraph(source, 'product-hook')
    target = first_body_paragraph(source, 'What changes') or first_class_paragraph(source, 'product-hook')
    deliverables = sentence_list(deliverable_names(source))
    extra = ''
    if route in STANDALONE_EXAMPLES:
        href, label = STANDALONE_EXAMPLES[route]
        extra = f'<p><a href="{href}">{escape(label)}</a></p>'
    return (
        '<section class="product-section worked-example-promo"><div class="shell"><div class="worked-example-promo-grid">'
        '<div class="worked-example-promo-copy"><p class="eyebrow">WORKED EXAMPLE</p><h2>SEE HOW THIS CAN WORK</h2>'
        f'<p><strong>Example situation:</strong> {escape(problem)}</p>'
        f'<p>House of Carol would examine the agreed current position, the evidence and inputs required for the {escape(title)}, and the bounded scope described on this page. The work would stay inside that defined problem rather than assuming a wider transformation.</p>'
        f'<p><strong>A clearer target state:</strong> {escape(target)}</p>'
        f'<p><strong>The customer could receive:</strong> {escape(deliverables)}.</p>'
        '<p class="worked-example-disclosure">Illustrative example — shown to explain how the service can be applied. It is not a customer testimonial or measured result.</p>'
        f'{extra}</div>'
        '<div class="worked-example-mini-flow" aria-hidden="true">'
        f'<div><span>Situation</span><p>{escape(problem)}</p></div>'
        f'<div><span>House of Carol examines</span><p>The agreed current position, relevant evidence and the bounded {escape(title)} scope.</p></div>'
        f'<div><span>Clearer state</span><p>{escape(target)}</p></div>'
        f'<div><span>Customer receives</span><p>{escape(deliverables)}.</p></div>'
        '</div></div></div></section>'
    )


def build_next_steps(route, titles):
    cards = []
    for target, condition, outcome in RELATIONS[route]:
        name = titles[target]
        cards.append(
            '<article class="worked-example-finding">'
            f'<h3>{escape(name)}</h3>'
            f'<p>If {escape(condition)}, this can help you {escape(outcome)}.</p>'
            f'<p><a href="{target}">Explore {escape(name)} →</a></p>'
            '</article>'
        )
    return (
        '<section class="product-section alt next-service-module"><div class="shell">'
        '<div class="product-section-heading"><h2>WHERE THIS COULD LEAD NEXT</h2>'
        '<p class="section-lead">This service is complete in its own right. If the work identifies a separate problem worth solving, these are the most likely next steps.</p></div>'
        '<div class="product-section-body"><div class="worked-example-findings">'
        + ''.join(cards) +
        '</div><p><strong>If the work resolves the problem and no separate need remains, no further House of Carol service is needed.</strong></p>'
        '<p>Not sure what follows? You do not need to choose another service now. Start with the problem in front of you.</p>'
        '</div></div></section>'
    )


def standardise(route, titles):
    path = ROOT / route
    source = path.read_text(encoding='utf-8')
    receive_start, receive_end = section_bounds_for_heading(source, 'What you will receive')
    defined_start, _ = section_bounds_for_heading(source, 'A defined engagement')
    if not (receive_end <= defined_start):
        fail(f'{route}: invalid deliverables/defined-engagement order')
    title = titles[route]
    source = source[:receive_end] + build_worked_example(route, source, title) + build_next_steps(route, titles) + source[defined_start:]
    count = source.count('class="identity-banner"')
    if count == 0:
        disclosure_start = source.find('<section class="product-section disclosures-section">')
        if disclosure_start < 0:
            fail(f'{route}: disclosure section missing for identity insertion')
        source = source[:disclosure_start] + IDENTITY_BANNER + source[disclosure_start:]
    elif count != 1:
        fail(f'{route}: identity banner count {count}')
    path.write_text(source, encoding='utf-8')


if len(PRODUCTS) != 54 or len(set(PRODUCTS)) != 54:
    fail('current product list must contain exactly 54 unique routes')
if set(RELATIONS) != set(PRODUCTS):
    missing = sorted(set(PRODUCTS) - set(RELATIONS))
    extra = sorted(set(RELATIONS) - set(PRODUCTS))
    fail(f'relationship-map mismatch; missing={missing}, extra={extra}')
for route, relations in RELATIONS.items():
    if not 1 <= len(relations) <= 3:
        fail(f'{route}: expected 1-3 adjacent recommendations')
    targets = [target for target, _, _ in relations]
    if route in targets:
        fail(f'{route}: self recommendation')
    if len(targets) != len(set(targets)):
        fail(f'{route}: duplicate recommendation target')
    for target in targets:
        if target not in PRODUCTS:
            fail(f'{route}: non-current recommendation target {target}')

for route in PRODUCTS:
    if not (ROOT / route).exists():
        fail(f'missing product route {route}')

titles = {route: first_h1((ROOT / route).read_text(encoding='utf-8')) for route in PRODUCTS}
if any(not title for title in titles.values()):
    fail('one or more current product routes has no readable H1')

for route in PRODUCTS:
    standardise(route, titles)

# The previous build generated 54-product-era standalone synthetic/composite case-study pages.
# This commission deliberately retires that layer. Remove any stale generated
# artefacts in the workspace so QA and Pages cannot accidentally publish them.
for generated in ROOT.glob('case-study-*.html'):
    generated.unlink()
index = ROOT / 'case-studies.html'
if index.exists():
    index.unlink()

print('PASS: built one evidence-honest inline worked-example and one conditional next-service module across all 54 current DEVELOP product pages; retained only explicit current product routes and removed the superseded generated legacy case-study layer from the build workspace')
