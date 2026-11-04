---
name: launch-watch
description: >-
  Builds the post-launch plan for keeping an eye on a live app: what to monitor
  (uptime, errors, slow pages, signup and payment funnel, failed payments, cost per
  user, abuse), which tools fit the stack and have free tiers, alert thresholds, a
  day-one / week-one / day-thirty routine, an incident playbook and a monthly review.
  Can generate starter snippets (health endpoint, error tracking, uptime checks).
  Use when the user says "what do I do after launch", "how do I monitor my app",
  "what should I watch", "set up alerts", "post-launch plan", or "keep an eye on
  things".
argument-hint: "[stack or host]"
---

# launch-watch

Launching is the start. This skill gives the owner a small, sustainable routine so
problems are found by them first, not by customers.

Writes `launch/watch.md`, `launch/monitoring/`, and merges groups into
`launch/checklist.json`.

## Step 1: choose the signals

Read `launch/inventory.json` and `launch/pricing.md` (if any). Pick only what applies:

| Signal | Why | Typical threshold |
| --- | --- | --- |
| Uptime of the home page and `/health` | Is it up? | alert after 2 failed checks (about 2 to 5 min) |
| Error rate and new error types | Is it broken? | any new error type; spike over 5x normal |
| Slow responses (p95) | Does it feel broken? | p95 over 2 s for 10 min |
| Signup to activation funnel | Is the product working for people? | activation under what you saw in beta |
| Checkout success / failed payments | Is money flowing? | any failed webhook; failure rate over 5% |
| Webhook delivery failures | Do payments grant access? | any failing endpoint in the provider dashboard |
| Cost per user / API spend | Will usage bankrupt you? | spend over 2x forecast in a day; hard cap set |
| Abuse (signups from one IP, burst of requests, spam content) | Bots show up day one | rate-limit hits, signup bursts |
| Database size, connections, backups | Quiet failures | backup missing 24 h; 80% of plan limits |
| Domain and certificate expiry | Silent outage | 30 days before |

## Step 2: tools by stack (free tiers exist; check current limits)

Recommend one per need, never everything:
- **Errors**: Sentry, or the host's built-in logs for tiny apps.
- **Uptime**: Better Stack, UptimeRobot, or the host's checks.
- **Product analytics / funnel**: PostHog, Plausible (cookieless, simpler legally),
  or the provider's own dashboards for revenue (Stripe).
- **Logs**: the host's log viewer first; a log service only when needed.
- **Cost**: billing alerts on every cloud/API account; provider usage caps.
- **Database**: the provider's metrics and backup status page.

State that pricing and free tiers change and link the official pages when you can.

## Step 3: generate starter snippets (ask first, then add files)

From `templates/` adapt to the stack: a health endpoint, error-tracking init, the
uptime-check list, alert rules. Put adapted copies under `launch/monitoring/`; only
touch project code if the owner approves (then hand off to `/launch-fix` recipes
`health-endpoint` and `error-tracking`).

## Step 4: write `launch/watch.md`

1. **Dashboard in one place**: the 5 links to open every morning.
2. **Alerts**: each alert, threshold, where it goes (a channel the owner will see on a
   phone), and what to do when it fires.
3. **Routine**:
   - **Launch day (hourly for the first few hours)**: errors, signups, payments,
     spend.
   - **Week one (daily, 10 minutes)**: errors, failed payments, support messages,
     funnel, cost, abuse, a read-through of 5 real user sessions or reports.
   - **Day 30 (one hour)**: what broke, what users asked for, churn and refunds,
     cost per user vs price (re-run `launch-pricing` numbers with real data),
     dependency updates, backup restore test, re-run `/launch` and compare scores.
   - **Monthly (30 minutes)**: the same review, shorter.
4. **Incident playbook** (from `templates/incident-playbook.md`): detect, stop the
   bleeding (pause signups, disable the broken feature, roll back), tell users
   plainly, fix, write down what happened and one change to prevent it.
5. **What to ignore**: vanity numbers, one-off blips, alerts that never lead to action
   (delete or tune them).

## Rules

- Few alerts the owner will act on beat many they will mute.
- Never put secrets in snippets (DSNs and keys come from env vars; use placeholders).
- Collect the least personal data you can; mention consent where analytics need it.
- Recommendations name trade-offs, not just brands.

## Output

`launch/watch.md`, `launch/monitoring/*`, updated `launch/checklist.json`.
