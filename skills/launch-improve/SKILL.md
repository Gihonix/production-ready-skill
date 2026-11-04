---
name: launch-improve
description: >-
  Suggests concrete improvements to a project and enforces the business and logical
  gaps that code audits miss: no clear buyer or promise, a price below cost, claims
  the product does not back up, no support or refund path, no way to measure or hear
  from users, no acquisition plan, features that contradict each other. Essential
  gaps are scored and can hold the verdict at Almost; suggestions never do. Use when
  the user says "how can I improve this", "what business gaps do I have", "is my
  idea logically sound", "what am I missing besides code", "suggest improvements",
  "sanity check my business", or as a stage between /launch-logic and /launch-verdict.
argument-hint: "[project folder]"
---

# launch-improve

`launch-gaps` asks "is the code safe?". `launch-logic` asks "does the money flow
work?". This skill asks the question before both: "would a stranger understand it,
trust it, pay for it, get help, and would you ever find out if it failed?"

Read-only on the project. Writes `launch/improve.json` and `launch/improve.md`.

## Inputs

Read what exists; do not stop if something is missing, mark the dependent check
`UNKNOWN` instead:

- `launch/context.json`, `launch/inventory.json`, `launch/map.md` (scan)
- `launch/findings.json`, `launch/logic.json`, `launch/pricing.json` (earlier stages)
- the project's README, landing page copy, pricing page, legal pages, `package.json`
  or equivalent description fields

If `context.json` has no answers for audience, money or personal data, ask the owner
the minimum (one message): who is it for, what do they pay, what happens if it breaks.

## Step 1: enforce the essentials

Walk the catalog in [`essentials.md`](essentials.md) (BIZ-01 and onward). For each item
decide `PASS`, `FAIL`, `UNKNOWN` or `NA` using evidence from the project itself:
a file and line, a page, a copy string, or a config value. An owner's verbal claim
("yes we have a refund policy") is `UNKNOWN` until it exists in writing somewhere you
can point to.

Severity follows the catalog, then context raises it: taking money, holding personal
data or serving businesses promotes legal, support and refund items to `blocker`.

## Step 2: hunt for logical gaps

Essentials are things that should exist. Logical gaps are things that exist but do
not agree with each other. Cross-check at least:

- **Promise vs product**: every headline claim on the landing page maps to a built
  feature. List claims with no feature behind them.
- **Price vs cost**: the price covers the cost to serve in `pricing.json` (or a stated
  estimate) at the expected usage, including free users.
- **Audience vs flow**: the onboarding asks for what this audience has (a solo
  hobbyist should not face a "request a demo" wall; an enterprise buyer will not
  paste a card into a self-serve form).
- **Free vs paid line**: the free tier lets a user reach first value but not finish
  the job; a free tier that already does the whole job never converts.
- **Terms vs behaviour**: the privacy page matches what the code actually collects
  (analytics, third-party SDKs, AI providers that receive user content).
- **Pricing page vs checkout**: plan names, limits and prices agree everywhere.
- **Metrics vs decisions**: whatever the owner says they will watch is actually
  measured (see BIZ-12).

Record each as a `gap` with the two things that disagree, both cited.

## Step 3: suggest improvements

Suggestions are advice, not enforcement. Offer at most 10, ranked by value over
effort, each a single sentence of change plus why and the rough effort (`S` under an
hour, `M` a day, `L` more). Prefer changes that raise the chance a stranger converts
or returns: a clearer first screen, a shorter path to first value, social proof the
owner already has, a sharper free-tier limit, an onboarding email, a cancel survey.
Do not suggest rewrites or new features unless a gap forces them.

## Step 4: write the outputs

`launch/improve.json`:

```json
{
  "issues": [
    {"id": "BIZ-03", "kind": "gap", "area": "business", "severity": "blocker",
     "status": "FAIL", "title": "No refund or cancellation terms anywhere",
     "why": "Buyers and card networks expect one; disputes cost fees and trust.",
     "evidence": [{"file": "app/pricing/page.tsx", "line": 41}],
     "fix_tier": "manual", "fix_id": null},
    {"id": "IMP-01", "kind": "suggestion", "area": "business", "severity": "nice",
     "status": "FAIL", "title": "Put the 30-second demo above the fold",
     "why": "Visitors decide in seconds; a demo shows value without reading.",
     "effort": "S", "value": "high"}
  ]
}
```

- `kind: "gap"` (ids `BIZ-nn`, from the catalog, plus `LOGIC-nn` for cross-check
  gaps) is **enforced**: `launch-verdict` reads it, so an open blocker holds the
  verdict below Ready.
- `kind: "suggestion"` (ids `IMP-nn`) is never scored and never changes the verdict.

`launch/improve.md`, in this order: a one-paragraph read of the business in plain
words; **enforced gaps** (blockers first, each with "what a stranger would
experience" and "what clears it"); **logical gaps**; **top suggestions**; the
`UNKNOWN`s the owner can settle in five minutes by pointing at where the thing lives.

## After running

1. Tell the owner how many enforced blockers there are and which one to clear first.
2. Re-run `/launch-verdict` so the gaps count; if there is no earlier run, say so.
3. Offer `/launch-roadmap` to turn the open items into a dated plan.

## Rules

- Every `FAIL` and `PASS` needs evidence; otherwise `UNKNOWN`.
- Stay inside what the project and the owner's answers show. No market-size,
  funding or valuation opinions, and no legal or financial advice: for legal items,
  say a page is missing and that a professional should review it.
- Enforcement is deliberately light: gaps count in the verdict like any finding,
  they do not block the owner from launching. Say plainly that launching with open
  gaps is the owner's call.
- Do not edit project code. Writing missing business pages is `launch-fix` or the
  owner's job.
- Never print secret values.

## Output

`launch/improve.json`, `launch/improve.md`.
