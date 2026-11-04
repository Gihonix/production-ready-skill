---
name: launch-gaps
description: >-
  Audits a project against a launch checklist and reports what is missing, with proof.
  Covers security, payments, data and backups, reliability, legal pages, SEO,
  accessibility, performance and config. Every item is PASS, FAIL or UNKNOWN with
  file and line evidence, ranked blocker / should-fix / nice-to-have. Use when the
  user says "what am I missing", "is it safe to launch", "launch checklist", "audit my
  app", "production readiness", "find gaps", or as step two of /launch.
argument-hint: "[project folder]"
---

# launch-gaps

The checklist the owner doesn't have in their head, run against their real code.

Read-only on the project. Writes only to `launch/`.

## Step 1: mechanical pass

Needs `launch/inventory.json` (run `/launch-scan` first) and ideally
`launch/context.json`.

```bash
python3 "${CLAUDE_SKILL_DIR}/checks.py" . --context "$(cat launch/context.json 2>/dev/null || echo '{}')"
```

This writes `launch/findings.json`: one entry per catalog item with `status`
(`PASS | FAIL | UNKNOWN | NA`), `severity`, `evidence` (file/line, never secret
values), `fix_tier` and `fix_id`. The full list is in `checklist.md`; stack-specific
guidance is in `stacks/`.

## Step 2: confirm every heuristic

Anything with `"needs_confirm": true` is a pattern match, not a verdict. For each:

1. Open the cited file and read the surrounding code. Check the real thing:
   - **SEC-04**: does the route verify a session/token AND that the record belongs to
     the caller? A login check without an owner check is still a data leak.
   - **SEC-05/06**: is it handled at the host or CDN instead (vercel.json,
     netlify.toml, Cloudflare)? If you can see that, PASS with the file as evidence.
   - **PAY-01**: signature check must use the raw request body, not parsed JSON.
   - **SEC-10**: RLS enabled AND policies written for each table.
2. Set the final `status` in `findings.json`, clear `needs_confirm`, and put your
   reasoning in `note`. If you cannot tell, leave `UNKNOWN`. Never promote to PASS
   without evidence.
3. Load `stacks/<name>.md` for each detected stack and run the extra checks it lists.
   Add new findings with ids like `STK-NEXT-01` using the same fields.

## Step 3: the non-mechanical items

Items with `mechanical: false` (backups, dependency audit, live-mode keys, email DNS,
rollback, timeouts, plan enforcement) come back `UNKNOWN`. Resolve what the code can
answer (read the paid routes for PAY-03; run `npm audit`, `pip-audit` or equivalent if
installed for SEC-11, and report counts, not the whole dump). For the rest, ask the
owner one short question each ("Is automatic backup switched on in your database
dashboard? Have you ever restored one?"), and record the answer. A claim without
evidence is `PASS` only if the owner says they verified it; note "owner-confirmed".

## Step 4: write `launch/gaps.md`

1. **Summary line**: counts by severity and status.
2. **Blockers** first, then should-fix, then nice-to-have. For each: the title, one
   plain sentence on why it matters to a non-expert, `file:line` evidence, the fix
   tier (auto / guided / manual) and roughly how long it takes.
3. **Unverified** section: what could not be checked and exactly how to check it.
4. **Passing** list in one compact block, so the owner sees what is already good.

## Rules

- Evidence or it didn't happen. FAIL cites file:line; unverifiable is UNKNOWN.
- Never write a secret value into any file or message. Location and type only.
- Severity can rise with context (money, personal data) but never falls to hide a
  problem. The catalog already escalates; do not downgrade a blocker without a
  written reason in `note`.
- Legal items are templates-and-pointers, not legal advice: say "have a professional
  review".
- Do not edit project code here. Fixes belong to `/launch-fix`.

## Output

`launch/findings.json` (final statuses), `launch/gaps.md`.
