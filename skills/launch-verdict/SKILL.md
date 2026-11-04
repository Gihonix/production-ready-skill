---
name: launch-verdict
description: >-
  Computes the go/no-go answer for launching: Ready, Almost, or Not yet. The verdict
  is calculated by a script from the findings, never written by hand, with a
  readiness score, a confidence score, per-area scores, the top five fixes and a
  plain answer to "is it safe to soft-launch?". Use when the user says "am I ready to
  launch", "can I go live", "give me the verdict", "launch score", or at the end of
  /launch-gaps.
argument-hint: "[project folder]"
---

# launch-verdict

One honest answer the owner can trust, because a script produced it from evidence.

## Run

```bash
python3 "${CLAUDE_SKILL_DIR}/verdict.py" .
```

Reads `launch/findings.json` (and `launch/logic.json` if present). Writes
`launch/verdict.json`, `launch/verdict.md`, and appends a point to
`launch/history.json` so progress can be charted. Use `--no-history` for dry runs.

## How the verdict is decided

| | |
| --- | --- |
| Weights | blocker 5, should 2, nice 1; `NA` ignored |
| Readiness | share of weight that PASSES (FAIL and UNKNOWN earn nothing) |
| Confidence | share of weight that was actually verified (not UNKNOWN) |
| **Ready** | zero open blockers (FAIL or UNKNOWN) and readiness 80+ |
| **Almost** | 1 to 3 open blockers, or no blockers but readiness under 80 |
| **Not yet** | more than 3 open blockers |

Unverified blockers keep the verdict from reaching Ready on purpose: "I haven't checked
whether backups work" is not the same as "backups work".

## After running

1. Read `launch/verdict.md` to the owner in plain words: the verdict, the two or
   three things that most change it, and the rough time to clear the blockers.
2. Add a short **"What would flip this to Ready"** paragraph under the generated
   text in `verdict.md` (the script's text stays; append only).
3. Offer the next step: `/launch-fix` to clear the fixable items, `/launch-report`
   for the visual dashboard.

## Rules

- Never edit the verdict, scores or counts by hand. To change them, change the
  findings (with evidence) and re-run.
- If a status was changed to PASS without evidence, revert it and say so.
- Do not soften "Not yet". If the owner pushes back, point to the specific open
  blockers and what clears each.
- Not a guarantee of safety, not a penetration test, not legal advice.

## Output

`launch/verdict.json`, `launch/verdict.md`, `launch/history.json`.
