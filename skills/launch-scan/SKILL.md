---
name: launch-scan
description: >-
  Explains what an AI-built project actually contains, in plain language. Detects the
  stack, pages, API routes, database tables, auth, payments, third-party services,
  environment variables, tests, CI and deploy config, and writes an inventory plus a
  readable tour. Use when the user says "what did the AI build", "explain my project",
  "what's in my app", "scan my project", "map my codebase", or as the first step of
  /launch.
argument-hint: "[project folder]"
---

# launch-scan

People who vibe-coded an app often can't say what it contains. This skill answers
that, so every later step works from facts and the owner finally knows what they have.

Read-only on the project. Writes only to `launch/` in the project root.

## Step 1: run the scanner

```bash
python3 "${CLAUDE_SKILL_DIR}/scan.py" . --out launch/inventory.json
```

Run from the project root (or pass the folder). It needs only Python 3.8+. It records
environment variable NAMES only, never values, and never opens `.env` files.

## Step 2: check it against reality

The scanner is pattern-based and can miss or mislabel. Before writing the tour:

1. Open the entry points (`package.json`, `app/` or `pages/`, `main.py`, `server.js`,
   the DB schema or migrations) and confirm the routes, tables and services listed.
2. Add anything it missed to `launch/inventory.json` (keep the same keys), for
   example a background job, a cron, a webhook, a file-upload path, an admin area.
3. If routes show `"auth": false`, do not conclude they are unprotected yet. That
   judgment belongs to `/launch-gaps`. Just record what you see.

## Step 3: write `launch/map.md`

Plain language for someone who did not write the code. No jargon without a gloss.

1. **In one paragraph**: what this app is and does, who it is for (infer from pages
   and copy; say "looks like" when unsure).
2. **What it's made of**: stack and each third-party service with what it is used for
   ("Stripe: takes payments", "Supabase: database and logins").
3. **What a visitor can do**: the pages and the main user journeys you can trace
   (sign up, log in, the core action, pay, cancel). Mark which of these were never
   built.
4. **Where the data lives**: tables/collections, what personal data they hold
   (emails, names, payment info, files), which are written by whom.
5. **Money and risk touchpoints**: anything that charges cards, calls a paid API
   (AI, SMS, email) or stores personal data. These drive launch priority.
6. **Environment variables**: the names the code needs, flagged `public` (shipped to
   browsers) vs `server-only`.
7. **What's missing at a glance**: no tests, no CI, no deploy config, no privacy
   page, and so on. One line each; details come from `/launch-gaps`.

Finish by asking the user 3 or 4 questions only if the code can't answer them (they
set the severity of later findings). Save answers in `launch/context.json`:

```json
{"takes_money": true, "personal_data": true, "uses_ai_api": false, "expected_users": "100 in month one"}
```

## Rules

- Evidence over guesses: cite `file:line` for claims about the code.
- Never print or copy secret values, even if you stumble on one. Say where it is.
- Do not edit project code here.

## Output

`launch/inventory.json`, `launch/map.md`, `launch/context.json`.
