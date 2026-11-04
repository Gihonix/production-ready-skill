---
name: launch-fix
description: >-
  Fixes what the launch audit found, safely. Works on its own git branch with one
  commit per fix, applies low-risk fixes in a batch after one approval, walks through
  riskier ones one by one with the diff, and gives step-by-step instructions for
  things that live outside the code. Re-checks each fix and re-computes the verdict.
  Use when the user says "fix these", "fix the blockers", "make it launch ready",
  "apply the suggestions", or after /launch-verdict.
argument-hint: "[finding ids, or 'blockers' | 'all-auto']"
---

# launch-fix

The only skill in the pack that edits project code. It is built so every change is
small, reviewed, tested and reversible.

## Preconditions

1. `launch/findings.json` exists with final statuses. If not, run `/launch-gaps`.
2. The project is a git repo with a clean working tree. If not clean, stop and ask
   the user to commit or stash. If it is not a repo, offer `git init` and an initial
   commit first; never fix an untracked project.
3. Create and switch to branch `launch-ready/fixes` (reuse it if it exists).

## Pick and order the work

Take the findings the user named; default to open blockers, then should-fix. Order:
security and secrets first, then payments, data, then everything else. Group by
`fix_tier`:

- **Auto**: low risk, mechanical. Show the full list of planned changes once and ask
  for ONE approval for the batch. Examples: `.gitignore` entries, `.env.example`,
  security headers, tighten CORS, health endpoint, robots/sitemap, meta tags, 404 and
  error pages, error-tracking starter, CI workflow, README run steps, template
  legal pages (marked "have a professional review before publishing").
- **Guided**: touches logic or needs a decision. For each one: explain the problem
  in a sentence, show the exact diff you propose, ask, apply on yes. Examples: add
  auth and ownership checks to routes, verify the payment webhook signature, make
  the webhook idempotent, enforce plan limits on the server, input validation,
  row-level security, migrations, account deletion, rate limiting that needs a store.
- **Manual**: outside the code. Never attempt these. Give numbered, copy-pasteable
  steps instead. Examples: rotate leaked keys, enable backups, DNS (SPF/DKIM/DMARC),
  switch payments to live mode, set host environment variables.

Recipes for common findings are in `fixes/<fix_id>.md`; read the recipe named in the
finding's `fix_id` before making the change, and adapt it to the project's stack and
style (match surrounding code, naming and comment density).

## For each fix

1. Make the smallest change that resolves the finding.
2. Run the project's own checks if they exist (`npm run build`, `npm test`,
   `pytest`, linter). If a check that passed before now fails, revert this fix
   (`git checkout -- .`), mark it `skipped` with the reason, and move on.
3. Re-run the relevant mechanical check:
   `python3 "${CLAUDE_SKILL_DIR}/../launch-gaps/checks.py" .` and look at that
   finding id. Only when it now reads PASS, set `"fixed": true` and `status: "PASS"`
   in `launch/findings.json`. If it still fails, say why and do not mark it fixed.
4. Commit that single fix: message `launch-ready: <finding id> <short title>`.

## Secrets

If a secret was committed or exposed: removing it from the code does NOT make it
safe. Always add the manual step "rotate this key now" (and "clean git history if the
repo is public or shared"). Never print the secret. Never write a real key into a
file; use placeholders in `.env.example`.

## Finish

1. Re-run `/launch-verdict` and `/launch-report` so the owner sees the before and
   after score.
2. Summarise: fixed (ids), skipped (ids and why), still needs a human (manual steps
   in order), and the new verdict.
3. Tell the owner how to undo: `git revert <commit>` for one fix, or delete the
   branch to drop all of them.

## Rules

- Never force-push, never deploy, never touch the main branch, never run
  destructive commands (`git reset --hard`, `rm -rf`, dropping tables).
- Never change production data or settings; code and config in the repo only.
- One approval covers only what was listed. A new kind of change needs a new
  approval.
- Do not "fix" a finding by suppressing the check or hiding the evidence.
- Legal text is a starting template, not legal advice.

## Output

Commits on `launch-ready/fixes`, updated `launch/findings.json`, `launch/fixes.md` (log of
what changed and what remains).
