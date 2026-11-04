---
name: launch
description: >-
  Gets an AI-built project to a confident go-live. Understands what the project
  contains, finds the gaps with evidence, reviews business logic, recommends pricing
  from competitor data, computes a Ready / Almost / Not yet verdict, fixes what can be
  fixed safely, and hands over a launch-day runbook and a post-launch watch plan, with
  a visual report. Use when the user says "am I ready to launch", "launch my app", "is
  my vibe-coded project production ready", "go live checklist", "what am I missing
  before launch", "/launch", or starts the launch-ready pack.
argument-hint: "[--quick] [project folder]"
---

# launch

The orchestrator for the launch-ready pack. Its job: replace "I hope it's fine" with a
verdict the owner trusts, then a plan for after.

Everything it writes goes to `launch/` in the project. The only stage that edits code
is `launch-fix`, with approval.

## Stages

| # | Skill | Question it answers | Writes |
| --- | --- | --- | --- |
| 1 | `launch-scan` | What did the AI actually build? | `map.md`, `inventory.json`, `context.json` |
| 2 | `launch-gaps` | What is missing or unsafe, with proof? | `findings.json`, `gaps.md` |
| 3 | `launch-logic` | Does the business actually work? | `logic.json`, `logic.md` |
| 4 | `launch-improve` | What business and logic gaps are there, and what would make it better? | `improve.json`, `improve.md` |
| 5 | `launch-pricing` | What should I charge? | `pricing.md`, `pricing.json` |
| 6 | `launch-verdict` | Can I go live? | `verdict.json`, `verdict.md`, `history.json` |
| 7 | `launch-fix` | Fix what you found | commits on `launch-ready/fixes` |
| 8 | `launch-report` | Show me | `report.html` |
| 9 | `launch-roadmap` | What do I do each day until launch? | `roadmap.json`, `roadmap.md`, a design in OpenFrame |
| 10 | `launch-day` | How do I go live safely? | `runbook.md` |
| 11 | `launch-watch` | What do I watch after? | `watch.md`, `monitoring/` |

`--quick` runs stages 1, 2, 6 and 8 only: a verdict and a picture in a few minutes.

## How to run it

1. **Orient** (2 minutes): confirm the project folder, create `launch/` and add it to
   `.gitignore` suggestion (not forced). Ask only what the code can't tell:
   - Who is it for and how many users do you expect in month one?
   - Will it take money? Will it hold personal data (emails, names, files)?
   - Does it call paid APIs (AI, SMS, email)?
   - Where will it be hosted?
2. Run stages in order, invoking each skill (`/launch-scan` and so on). Between stages,
   give the owner one or two plain sentences on what was found. Keep the tone calm:
   most vibe-coded apps have fixable gaps; the point is to see them.
3. After stage 6, stop and show the verdict. Ask what to do next: fix the blockers
   (stage 7), see the report (8), plan the days to launch (9), or go straight to the
   runbook (10).
4. After fixes, re-run stages 2, 4, 6 and 8 so the owner sees the score move.
5. Finish with `launch-roadmap` (ask how many days), `launch-day` and `launch-watch`. End with the one thing to do first
   tomorrow morning.

## Honest limits (say them once, early)

- This reads code and config; it cannot see your dashboards, DNS or live data, so some
  items are "unverified" until you confirm them. Unverified is never counted as passed.
- It is not a penetration test, a security certification or legal/financial advice.
  For handling payments or health/financial data at scale, get a professional review.
- Heuristics can be wrong in both directions; every finding cites where to look.

## Rules

- Evidence or it didn't happen. Never mark something PASS without proof.
- Never print secret values, anywhere.
- Never deploy, never change production, never force-push.
- The verdict is computed by `launch-verdict`; never state one by hand.
- If a stage's skill is not installed, say which one and continue with the rest.

## Output

The `launch/` folder (above) and a closing summary: verdict, readiness and confidence,
what changed this session, what the owner must still do themselves, and the next review
date.
