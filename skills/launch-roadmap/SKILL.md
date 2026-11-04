---
name: launch-roadmap
description: >-
  Asks how many days until launch and turns the open audit findings into a day-by-day
  roadmap: Day 1, Day 2, and so on up to Launch Day, saying what to do each day, how
  long it takes and when each day is done. Designs the roadmap as a visual in
  OpenFrame first and only builds it into the report after the owner approves. Use
  when the user says "make a launch roadmap", "I want to launch in 7 days", "what do
  I do each day", "launch timeline", "plan my launch week", or after /launch-verdict
  or /launch-improve.
argument-hint: "[days until launch] [project folder]"
---

# launch-roadmap

A verdict says where you stand. A roadmap says what to do on Monday.

Writes `launch/roadmap.json` and `launch/roadmap.md`. Read-only on the project's code.

## Step 1: ask for the duration

Ask these, in one message, and wait:

1. **How many days until you want to launch?** Count Launch Day itself: "7" means six
   preparation days and Launch Day on the seventh. Accepts 1 to 90.
2. **How many hours a day can you realistically work on it?** Default 4.
3. **Do you have a date for Day 1?** Optional; with it the roadmap shows real dates.

If the argument already gives the days, do not ask again; still confirm hours.

If `launch/verdict.json` is missing, say the plan will have no audit behind it and offer
to run `/launch --quick` first. Run the plan anyway if the owner says so.

## Step 2: build the plan

```bash
python3 "${CLAUDE_SKILL_DIR}/roadmap.py" . --days <N> --hours <H> [--start YYYY-MM-DD]
```

It reads `findings.json`, `logic.json`, `improve.json` and `verdict.json`. Every open
item (FAIL or UNKNOWN) becomes a task with a time estimate, blockers first. The shape
of the plan is fixed and the script does the scheduling, not you:

| Day | Purpose |
| --- | --- |
| Day 1 to Day N-4 | Preparation: close blockers, then business gaps, then should-fix |
| Day N-3 (when N is 4 or more) | Go-live checks: domain, production variables, live payments, email DNS, monitoring, spend caps |
| Day N-1 (when N is 2 or more) | Rehearsal: freeze, restore a backup, roll back once, smoke test, strangers sign up cold |
| **Launch Day** | Go/no-go gate, deploy, smoke test, announce small then wide, watch the first hour |

Blockers are never pushed past launch. If they do not fit, the plan runs over capacity
and a warning says by how much. Should-fix and nice-to-have items that do not fit are
listed as "moved to after launch". Do not reshuffle the output by hand; to change the
plan, change the days, the hours or the findings and re-run.

## Step 3: tell the owner what it means

In plain words, not the whole file: how many days, what Day 1 starts with, whether it
fits, and any warning (over capacity, a one-day plan, no audit). If it does not fit,
give the two honest choices: add days or hours, or launch smaller (a private beta)
with the named blockers open.

## Step 4: show it

The visual template is fixed and already approved (designed once in OpenFrame, now
built into `launch-report`). Do not use OpenFrame or any design tool for a normal run.

```bash
python3 "${CLAUDE_SKILL_DIR}/../launch-report/report.py" .
```

This adds a "Launch roadmap" panel to `launch/report.html`: a header with hours per
day, one row per day with tickable tasks, a rehearsal row, a timed Launch Day run
sheet and an after-launch strip. Tell the owner where to open it.

Only if the owner explicitly asks for a different look, change the template in
`report.py` (and, if they want to see it first, mock it up in a design tool they
name). That is a one-off request, not part of the skill.

## Rules

- Never schedule Launch Day on top of an open blocker silently: the warning stays.
- Never run deploy, DNS or payment commands. Launch Day tasks are the owner's to do.
- Do not invent tasks that the audit and the fixed plan do not contain. Extra advice
  goes to `launch-improve`.
- Estimates are rough and assume one person; say so.

## Output

`launch/roadmap.json`, `launch/roadmap.md`, and the roadmap section of
`launch/report.html`.
