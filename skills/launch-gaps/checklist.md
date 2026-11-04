# Launch checklist

Generated from `CATALOG` in `checks.py`. Do not edit by hand; add items there.

## Security

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| SEC-01 | blocker | No .env file committed to the repo | Anyone with repo access (or a leak) gets your real keys and can run up your bills or read your data. | guided | List tracked env files; rotate any keys that were committed. |
| SEC-02 | should | .gitignore excludes .env files | Without it, the next `git add .` commits your secrets. | auto | .gitignore contains .env* |
| SEC-03 | blocker | No secrets hard-coded in source | Keys in code end up in git history and, for frontend code, in every visitor's browser. | guided | Grep for key patterns; rotate anything found. |
| SEC-04 | blocker | Every API route that changes or reveals user data checks who is calling | An unprotected route lets anyone on the internet read or edit other users' data. | guided | Read each flagged route; confirm it verifies a session/token and the owner of the record. |
| SEC-05 | should | Rate limiting on login, signup and expensive routes | Bots can brute-force passwords, spam you, or burn paid API credits within hours of launch. | auto | Look for a rate-limit library or provider setting. |
| SEC-06 | should | Security headers set (CSP/HSTS/X-Frame-Options etc.) | Cheap protection against clickjacking, MIME sniffing and some XSS. | auto | helmet / headers() / middleware |
| SEC-07 | should | CORS is not open to every origin | A wildcard CORS policy lets any website call your API from your users' browsers. | auto | origin '*' / allow_origins ['*'] |
| SEC-08 | blocker | Debug mode is off for production | Debug mode exposes stack traces, internal paths and sometimes an interactive console. | auto | DEBUG=True / debug=True |
| SEC-09 | should | User input is validated on the server | Without validation, malformed or hostile input reaches your database and crashes things. | guided | zod/joi/pydantic/etc. used on API inputs |
| SEC-10 | blocker | Database access rules (row-level security) are enabled | With Supabase/Firebase, the browser talks to the database directly: no rules means anyone can read everything. | guided | RLS enabled + policies per table (also check the provider dashboard). |
| SEC-11 | should | Dependencies have no known critical vulnerabilities | Old packages are the most common way small apps get hacked. | guided | Run npm audit / pip-audit / equivalent and read the result. |
| SEC-12 | should | Server-only keys are not exposed to the browser | Variables prefixed NEXT_PUBLIC_/VITE_/REACT_APP_ are shipped to every visitor. | guided | Look for secret-looking names in public env vars. |

## Payments

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| PAY-01 | blocker | Payment webhooks verify the signature | Without it anyone can POST a fake 'payment succeeded' and get your product free. | guided | constructEvent / construct_event in the webhook handler. |
| PAY-02 | should | Webhook handling is idempotent (same event twice = one effect) | Payment providers retry; duplicates can double-grant credits or double-send emails. | guided | Event ids stored/checked before acting. |
| PAY-03 | blocker | Paid features are enforced on the server, not only hidden in the UI | Hiding a button is not access control: free users can call the API directly. | guided | Read paid-feature routes for a plan/subscription check. |
| PAY-04 | should | Failed payment and cancellation paths exist | Cards fail and customers cancel every week. Without handling, access and billing drift apart. | guided | Handlers for invoice.payment_failed / subscription.deleted. |
| PAY-05 | blocker | Live-mode keys and webhook secret configured for production (not test keys) | Test keys in production mean you take no real money; live keys in dev risk real charges. | manual | Check hosting env vars and provider dashboard. |

## Data

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| DATA-01 | blocker | Automatic database backups are on and a restore was tried | One bad migration or deleted table can end the business without a backup you've actually restored. | manual | Provider dashboard: backups/PITR. |
| DATA-02 | should | Database schema changes are tracked as migrations | Hand-edited production databases drift and can't be rebuilt or rolled back. | guided | migrations dir / prisma migrate / alembic / supabase/migrations |
| DATA-03 | should | Users can delete their account/data | Privacy laws (GDPR/CCPA) expect it, and users ask within weeks. | guided | Search for delete-account flow. |

## Reliability

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| REL-01 | should | Errors are reported to a tracker (Sentry or similar) | Without it you learn about crashes from angry users, if at all. | auto | sentry in dependencies/config |
| REL-02 | should | A health-check endpoint exists | Uptime monitors and hosts need one URL that says 'I'm alive'. | auto | /health, /api/health, /healthz, /ping |
| REL-03 | should | Automated tests exist for the critical paths | Without tests, every AI edit after launch can silently break signup or payment. | guided | tests dir / test runner |
| REL-04 | should | A CI pipeline runs build/tests on every push | Catches broken builds before users do. | auto | .github/workflows or equivalent |
| REL-05 | should | A dependency lockfile is committed | Without it, production can install different versions than you tested. | auto | package-lock.json / pnpm-lock.yaml / poetry.lock etc. |
| REL-06 | nice | Friendly 404 and error pages | A raw stack trace or blank page at launch looks broken and leaks details. | auto | not-found / error.tsx / 404.html |
| REL-07 | should | Outbound calls (APIs, AI, email) have timeouts and failure handling | One slow third party can hang every request or crash the server. | guided | Read the code around external calls. |

## Legal

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| LEG-01 | should | Privacy policy page exists | Required in most places once you collect emails or use analytics; payment/ad providers require it. | auto | page matching /privacy |
| LEG-02 | should | Terms of service page exists | Sets the rules for use, refunds and liability; expected by payment providers. | auto | page matching /terms |
| LEG-03 | should | Cookie/analytics consent where required | Analytics or ad cookies without consent can breach EU/UK rules. | guided | analytics present vs consent banner. |
| LEG-04 | should | Refund/cancellation policy is stated (if charging money) | Disputes and chargebacks follow when buyers can't find the rules. | auto | refund policy page or section |

## Seo

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| SEO-01 | should | Pages have a title, description and social preview tags | This is what Google and link previews show; blank means nobody clicks. | auto | metadata / <title> / og: tags |
| SEO-02 | nice | robots.txt and sitemap exist | Helps search engines find and index the right pages. | auto | robots.txt, sitemap.xml/ts |

## Accessibility

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| A11Y-01 | nice | Images have alt text | Screen-reader users and SEO both rely on it. | auto | <img> without alt |

## Performance

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| PERF-01 | nice | No oversized images/assets shipped | A multi-megabyte image makes the first visit slow on mobile. | guided | files >1MB in public/static/assets |

## Config

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| CFG-01 | nice | An .env.example documents required variables | The next person (or you in 3 months) can't deploy without guessing. | auto | .env.example present and complete |
| CFG-02 | nice | README explains how to run and deploy | Future you and any helper need it. | auto | README.md present with run steps |

## Auth

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| AUTH-01 | should | Password reset and email verification work (or a managed provider handles them) | Users who forget a password become support tickets or lost customers; unverified emails enable abuse. | guided | Provider (Clerk/Auth0/Supabase) or custom reset flow. |

## Email

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| EMAIL-01 | should | Sending domain has SPF, DKIM and DMARC | Otherwise your signup and receipt emails land in spam. | manual | DNS records for the sending domain. |

## Operations

| ID | Severity | Check | Why it matters | Fix | How to verify |
| --- | --- | --- | --- | --- | --- |
| OPS-01 | should | You can roll back a bad deploy | The first bad release will happen; you need a way back in minutes. | manual | Host rollback feature / tagged releases. |

