---
name: launch-report
description: >-
  Renders the launch audit as one visual, offline HTML dashboard: verdict banner and
  readiness gauge, top fixes, a radar of scores by area, a map of what the app
  actually contains with problem spots marked red, the user journey with missing
  steps highlighted, competitor price chart, filterable findings board, score
  history, and tickable launch and watch checklists. Use when the user says "show me
  a report", "dashboard", "visual summary", "something I can share", "make it
  visual", or at the end of /launch.
argument-hint: "[project folder]"
---

# launch-report

People trust what they can see. This turns the JSON from the other skills into a page
the owner can open, print to PDF or send to a cofounder.

## Run

```bash
python3 "${CLAUDE_SKILL_DIR}/report.py" .
```

Writes `launch/report.html`. It is self-contained: inline CSS and SVG, no CDN, no
network, works offline, supports dark mode and phone width. It needs
`launch/verdict.json` (run `/launch-verdict` first) and uses these when present:
`inventory.json`, `findings.json`, `history.json`, `logic.json`, `pricing.json`,
`checklist.json`.

## What it shows

- Verdict banner, readiness gauge, confidence, the five fixes to do first.
- Radar and table of scores by area (security, payments, data, legal, and so on).
- **What your app actually is**: pages, API routes, data tables and services drawn from
  the inventory; files with failing findings turn red with the finding id.
- User journey (from `logic.json`) with missing and weak steps highlighted.
- Competitor price bars, tiers and break-even (from `pricing.json`).
- Progress line across runs (from `history.json`): the score climbing as fixes land.
- Findings board filterable by severity and status, each with evidence and fix tier.
- Launch and watch checklists with tick boxes saved in the browser.

## After running

1. Tell the owner the path, and open it for them if the environment can (a browser
   pane, `open launch/report.html` on macOS, `xdg-open` on Linux, `start` on Windows).
2. If running inside Claude with the Artifact tool, offer to publish it as a private
   page for sharing. Do not publish without the owner's yes: the report names files
   and weaknesses.
3. Remind the owner the report describes weaknesses: share it only with people who
   should see them, and keep `launch/` out of public repos unless intended (the pack's
   `.gitignore` suggestion: add `launch/`).

## Rules

- Do not hand-edit the HTML; change the JSON and re-run.
- Never put secret values in any input file; the report prints what it is given.
- If a section's input is missing, it is skipped, not faked.

## Output

`launch/report.html`.
