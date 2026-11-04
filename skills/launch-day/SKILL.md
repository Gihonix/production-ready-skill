---
name: launch-day
description: >-
  Writes the go-live runbook: a pre-flight checklist (domain, SSL, production
  environment variables, DNS and email authentication, production database, payments
  in live mode), a ten-minute smoke test, a rollback plan, and the order of the
  announcement. Use when the user says "how do I go live", "launch checklist",
  "deploy to production", "launch day plan", "pre-flight", "what do I do on launch
  day", or after /launch-verdict says Ready or Almost.
argument-hint: "[host, e.g. vercel | netlify | fly | render | railway]"
---

# launch-day

Turns "I think it's ready" into a sequence of checkable steps with an owner and a way back.

Writes `launch/runbook.md` and merges a "Launch day" group into `launch/checklist.json`
(the report shows it as tickable boxes).

## Before writing

Read `launch/verdict.md`, `launch/inventory.json` (host, services, env vars) and
`launch/gaps.md`. If open blockers remain, say so at the top of the runbook and list
them; do not pretend the app is ready. The runbook is still useful as a plan.

## Runbook sections

1. **Go / no-go gate**: blockers cleared (list), backup restore tested (date), payments
   tested with one real small purchase and refund, someone other than the author
   has completed signup on a phone.
2. **Pre-flight**, grouped, each with "how to check":
   - **Domain and HTTPS**: domain points to production, certificate valid, `www` and
     bare domain both work, one redirects to the other, HTTP redirects to HTTPS.
   - **Environment**: every name from `inventory.json` `env_vars` set in the HOST
     (names listed, values never written down), production not using test keys,
     `NODE_ENV=production` / `DEBUG` off, `APP_URL`/redirect URLs set to the live
     domain in auth provider and payment provider settings.
   - **Database**: production DB is separate from dev, migrations applied, backups
     on, connection limits sensible, no seed/demo data.
   - **Email**: sending domain verified (SPF, DKIM, DMARC), test signup, receipt and
     reset emails land in the inbox.
   - **Payments**: live products, live webhook endpoint and secret, a real small
     purchase works and grants access, the refund path works.
   - **Third parties**: API quotas and spending limits set (AI, SMS, maps); budget
     alerts on the cloud account.
   - **Legal and trust**: privacy, terms, refund pages linked in the footer; contact
     email works; cookie notice if needed.
   - **Monitoring**: error tracking receiving a test error, uptime check on the
     health URL, alert goes to a channel the owner will actually see (see
     `/launch-watch`).
3. **Smoke test (10 minutes, after every deploy)**: open the home page; sign up with a
   fresh email; verify email; log in/out; do the core action; hit the paywall; pay with
   a real card (small amount) or the provider's live-mode test method; confirm access;
   cancel; log in on a phone; open a private page logged out and confirm it is
   refused. Tick each box; write down the time.
4. **Rollback plan**: the exact button or command to return to the previous deploy,
   who decides, how to put up a maintenance message, how database changes are kept
   backward-compatible for one release, whom to tell.
5. **Announcement order**: soft launch to 5 to 20 known people first, watch day-one
   metrics, fix, then widen. Suggested sequence: private beta, waitlist, then public
   post. Never announce before the smoke test passes.
6. **First hour**: what to watch (errors, signups, failed payments, cost dashboards),
   who is on call (the owner), when to pause (any payment or data bug).

Tailor host-specific steps to the detected platform (Vercel, Netlify, Fly, Render,
Railway, a VPS); if unknown, ask once.

## Rules

- Never run deploy or DNS commands yourself; this skill writes the plan, the owner
  executes it.
- Never write secret values into the runbook; names only.
- No claims you cannot verify (for example "SSL is fine"): phrase as a check to do.

## Output

`launch/runbook.md`, updated `launch/checklist.json`.
