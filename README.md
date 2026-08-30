# House of Carol — maturity preview

This repository is the current public-preview source for **House of Carol**.

## Current status

- GitHub Pages is enabled.
- The site is a controlled maturity preview and remains `noindex,nofollow`.
- Customer acquisition is paused until the House maturity gate returns GO.
- Identity/contact/legal fields deliberately remain placeholders: `[LEGAL NAME]`, `[SERVICE ADDRESS]`, `[HOC PUBLIC EMAIL]`.
- The site contains no enquiry form, payment facility, analytics, ad tracker or non-essential cookie.
- No product or service is currently represented as approved for sale.

## What changed in this maturity build

The previous workflow-improvement/£495 positioning is not current House strategy and must not be restored as the default business model. House of Carol is a portfolio business and may operate multiple lawful income streams.

The corporate site now does four jobs only:

1. identify House of Carol;
2. explain the portfolio model without promising an unvalidated offer;
3. demonstrate the customer-facing quality/trust standard;
4. provide a controlled shell into which validated venture pages can later be released.

## Engineering approach

The preview is intentionally static HTML/CSS with no package manager, framework, database or build step. This keeps the £0 hosting path simple and provides a direct manual recovery route.

Important files:

- `index.html` — corporate home;
- `portfolio.html` — multi-income-stream portfolio shell;
- `trust.html` — external standards;
- `privacy.html` and `terms.html` — placeholder-controlled legal pages;
- `assets/hoc-preview.css` — current presentation layer;
- `robots.txt` — blocks crawling while the maturity gate is closed.

Older repository assets remain historical only where they are not referenced by the current pages. Do not treat their content as current HOC authority.

## Release gate

Before customer acquisition or indexing is enabled:

- replace placeholders with CEO-approved HOC identity/contact details;
- approve at least one sale-ready venture with price, delivery, support and legal/privacy checks;
- complete the actual privacy and customer terms for the live stack;
- run accessibility, mobile, link and human-voice QA;
- test the enquiry-to-payment-to-delivery manual path;
- receive GO from the House maturity gate.

No secrets, bank details, customer-confidential data or personal Gmail content belong in this repository.
