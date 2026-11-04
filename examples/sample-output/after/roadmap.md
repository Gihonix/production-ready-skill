# Launch roadmap

3 day(s) to launch, 4 h/day of preparation.
Planned from verdict **Ready** (readiness 86).

## Day 1: Polish: Security, Payments
_Raise the score; nothing here blocks launch._  about 225 min

- [ ] Verify: Dependencies have no known critical vulnerabilities (should), ~45 min
- [ ] Verify: Webhook handling is idempotent (same event twice = one effect) (should), ~45 min
- [ ] Verify: Failed payment and cancellation paths exist (should), ~45 min
- [ ] Fix: Users can delete their account/data (should), ~45 min
- [ ] Verify: Outbound calls (APIs, AI, email) have timeouts and failure handling (should), ~45 min

Done when: Every task above ticked; Re-run /launch-gaps and /launch-verdict; score has not dropped

## Day 2: Rehearse
_Break it on purpose while it is still safe._  about 220 min

- [ ] Code freeze: only fixes for problems the rehearsal finds, ~10 min
- [ ] Restore last night's backup into a scratch database and open the app, ~45 min
- [ ] Rollback drill: deploy a harmless change, then roll back to the previous deploy, ~30 min
- [ ] Run the 10-minute smoke test end to end on a phone, ~30 min
- [ ] Have 3 to 5 people sign up cold; watch where they stall, do not help, ~60 min
- [ ] Write the announcement post and the first support-reply templates, ~45 min

Done when: Backup restored, rollback worked, a stranger finished signup; Announcement text is written

## Launch Day: Launch Day
_Ship it, watch it, learn from it._  about 165 min

- [ ] Go / no-go gate: blockers cleared, backup restored, someone else signed up, ~20 min
- [ ] Deploy to production (you press the button; nothing here deploys for you), ~20 min
- [ ] Run the 10-minute smoke test on production and write down the time, ~15 min
- [ ] Announce to the first small group, then widen (private beta, waitlist, public), ~30 min
- [ ] Watch errors, signups and payments for the first hour; answer every message, ~60 min
- [ ] Write down day-one numbers and the three things you would change first, ~20 min

Done when: Smoke test passes on production; You can see errors and signups as they happen

## Moved to after launch

- Verify: Password reset and email verification work (or a managed provider handles them) (should)
- Verify: Sending domain has SPF, DKIM and DMARC (should)
- Verify: You can roll back a bad deploy (should)
- Fix: Put a demo above the fold (nice)

## After launch

- **Day +1**: Read every error and support message; fix what blocks a new user
- **Week 1**: Review funnel: signup to first value to payment; pick one thing to improve
- **Day 30**: Re-run /launch, compare the score, plan the next month
