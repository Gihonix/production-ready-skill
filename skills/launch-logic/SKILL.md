---
name: launch-logic
description: >-
  Reviews the business logic of an AI-built app: the path from signup to value to
  payment to cancellation, whether paid features are really locked, abuse and cost
  risks, and the flows the AI never built (password reset, email verification, empty
  states, onboarding, refunds). Use when the user says "does my business logic work",
  "what flows am I missing", "can people cheat my pricing", "review my user flow", or
  as part of /launch.
argument-hint: "[project folder]"
---

# launch-logic

Code can be clean and the business still leak. This skill follows the money and the
user, not the syntax.

Read-only on the project. Writes `launch/logic.json` and `launch/logic.md`.

## Step 1: trace the journey

From `launch/inventory.json` and the code, trace each step and mark it `ok`, `weak`
(exists but fragile) or `missing`:

1. Land and understand (home page says what it is, who it is for, the next step).
2. Sign up (and email verification).
3. First value (the moment the user gets what they came for; how fast?).
4. Hit a limit or paywall.
5. Pay (checkout, receipt, access granted).
6. Use as a paying customer.
7. Payment fails / card expires.
8. Cancel, downgrade, delete account, get a refund.
9. Come back after forgetting the password.

## Step 2: attack the business model

Read the code for each question and cite `file:line`.

- **Plan enforcement**: pick each paid feature. Can a free user reach it by calling
  the API directly, guessing a URL or editing a request? Is the limit checked on the
  server?
- **Ownership**: can user A read or edit user B's records by changing an id?
- **Cost abuse**: every route that calls a paid API (AI, SMS, email, maps, storage)
  needs auth, a per-user quota and a rate limit. Estimate the worst-case bill if one
  bot hammers it for an hour.
- **Free abuse**: unlimited free trials by new emails, referral loops, free tier too
  generous to ever convert.
- **Money edge cases**: double click on pay, webhook arrives before redirect, retried
  webhook, price changes mid-subscription, currency, taxes, partial refunds.
- **State edge cases**: empty states, first-run, deleted user's data, two tabs, slow
  network, user closes the tab mid-action.
- **Email/notifications**: welcome, receipt, failed payment, password reset: sent
  from a verified domain? What if sending fails?
- **Admin**: how do you see users, refund someone, or ban an abuser without editing
  the database by hand?

## Step 3: write the outputs

`launch/logic.json` (read by verdict, fix and report):

```json
{
  "journey": [{"step": "Sign up", "status": "ok", "note": "Supabase auth"},
              {"step": "Cancel", "status": "missing", "note": "no cancel flow"}],
  "issues": [{"id": "LOG-01", "area": "logic", "severity": "blocker", "status": "FAIL",
              "title": "Free users can call /api/export, a paid feature",
              "why": "Anyone can use the paid feature without paying.",
              "evidence": [{"file": "app/api/export/route.ts", "line": 12}],
              "fix_tier": "guided", "fix_id": "enforce-plan-limits"}]
}
```

Issue ids are `LOG-nn`, stable across runs. Severity: **blocker** = loses money, leaks
data or locks paying users out on day one; **should** = fix within 30 days; **nice** =
polish.

`launch/logic.md`: the journey as a short list with the broken steps first, then the
issues in plain language, each with "what a user or attacker would do" and "what it
costs you".

## Rules

- Evidence for every issue; if you can only suspect it, mark `UNKNOWN` with the
  question to answer.
- Describe abuse at the level of "a user could do X" so the owner can fix it; no
  working exploit scripts.
- Missing flows count even though there is no code to cite: say "not built" and cite
  where it would belong.
- Do not edit project code here.

## Output

`launch/logic.json`, `launch/logic.md`.
