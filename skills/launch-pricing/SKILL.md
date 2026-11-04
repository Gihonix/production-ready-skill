---
name: launch-pricing
description: >-
  Recommends what to charge, using real competitor prices and the app's own cost to
  serve. Finds three to six competitors, records their public pricing with links,
  builds a comparison, models per-user cost and break-even with a script, and
  recommends a price, tiers, the free-vs-paid line and two prices to test. Use when
  the user says "how much should I charge", "pricing strategy", "what do competitors
  charge", "is my price right", "free vs paid", or as part of /launch.
argument-hint: "[current price]"
---

# launch-pricing

Founders guess price and usually guess low. This skill sets it from two things that
can be checked: what the market charges and what each customer costs to serve.

Self-contained. Web search makes it better; without web access, ask the user to paste
competitor pricing-page URLs or numbers.

## Step 1: know the product

From `launch/map.md` and `launch/inventory.json`: who is it for, what job does it do,
what does the user get at the first moment of value, and which features cost money to
run (AI calls, SMS, storage, email). Ask the user for the current or intended price
and the audience if the code doesn't say.

## Step 2: find competitors

Find 3 to 6 real alternatives for the same job: direct competitors, and the substitute
a buyer would use instead (a spreadsheet, an agency, doing it by hand). For each,
from their OWN public pricing page: plan names, price, billing period, what the plan
includes, free tier or trial, and the limit that forces an upgrade. Record the URL and
the date you read it.

Rules for this step:
- Public sources only. No invented prices: if a price is "contact sales", write that.
- Compare like with like (same period, same seats, same limits).
- Note what customers complain about in public reviews about price or limits when
  easy to find, with the link.

## Step 3: model your cost to serve

Per paying user per period, from the inventory and published provider prices
(link the pricing pages you used and state your assumptions about usage):
hosting share, database, AI/API calls per user, email/SMS, storage, support time.

```bash
python3 "${CLAUDE_SKILL_DIR}/cost_model.py" --price 19 --fixed 120 --variable 3.5 \
  --fee-pct 2.9 --fee-fixed 0.30 --users 100 --churn 5 --sweep 12,19,29
```

It prints contribution per user, margin, break-even users and profit at N users.
Show the owner the numbers at 2 or 3 candidate prices. If any price loses money per
user, say so plainly.

## Step 4: recommend

Write `launch/pricing.md`:

1. **The price** and why: where it sits among competitors, the margin it gives (from
   the script), what a customer gets for it.
2. **Tiers** (good / better / best, or free / pro): what is in each, and the exact
   limit or feature that makes people step up. Put the free-vs-paid line where
   value is felt but running cost is capped.
3. **Opening offer**: an intro price or bonus with an end date, one that does not
   train buyers to wait for discounts. No fake "was $X" anchors.
4. **Test plan**: two prices inside a sensible range and how to compare them with
   real buyers (two landing pages, a pre-sale at each, a waitlist asking "would you
   pay $X?"). Name the number that decides it.
5. **Risks**: a cost that scales with usage (set a usage cap or quota), annual vs
   monthly, refunds, taxes (check with a professional).

Also write `launch/pricing.json` for the report:

```json
{"currency": "$", "period": "month", "your_price": 19, "break_even_users": 8,
 "competitors": [{"name": "Acme", "price": 29, "url": "https://example.com/pricing"}],
 "tiers": [{"name": "Free", "price": 0, "includes": "3 projects"}]}
```

## Rules

- Every competitor figure has a link. Every cost figure has a stated assumption.
- Simulated or imagined buyers are not evidence. Real willingness to pay is.
- Never recommend pricing below variable cost to "win" customers without saying how
  long the business can afford it.
- This is a decision aid, not financial advice.

## Output

`launch/pricing.md`, `launch/pricing.json`.
