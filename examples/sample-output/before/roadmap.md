# Launch roadmap

7 day(s) to launch, 4 h/day of preparation.
Planned from verdict **Not yet** (readiness 9).

## Day 1: Close blockers: Security, Payments
_6 blocker(s) closed and re-checked._  about 235 min

- [ ] Fix: No .env file committed to the repo (blocker), ~45 min
- [ ] Fix: No secrets hard-coded in source (blocker), ~45 min
- [ ] Fix: Every API route that changes or reveals user data checks who is calling (blocker), ~45 min
- [ ] Fix: Database access rules (row-level security) are enabled (blocker), ~45 min
- [ ] Fix: Payment webhooks verify the signature (blocker), ~45 min
- [ ] Fix: Privacy policy page exists (blocker), ~10 min

Done when: Every task above ticked; Re-run /launch-gaps and /launch-verdict; score has not dropped

## Day 2: Close blockers: Payments, Data
_6 blocker(s) closed and re-checked._  about 235 min

- [ ] Verify: Paid features are enforced on the server, not only hidden in the UI (blocker), ~45 min
- [ ] Verify: Live-mode keys and webhook secret configured for production (not test keys) (blocker), ~30 min
- [ ] Verify: Automatic database backups are on and a restore was tried (blocker), ~30 min
- [ ] Fix: Refund and cancellation terms (blocker), ~45 min
- [ ] Fix: A way for users to reach you (blocker), ~45 min
- [ ] Fix: Terms of service page exists (blocker), ~10 min
- [ ] Fix: .gitignore excludes .env files (should), ~10 min
- [ ] Fix: Rate limiting on login, signup and expensive routes (should), ~10 min
- [ ] Fix: Security headers set (CSP/HSTS/X-Frame-Options etc.) (should), ~10 min

Done when: Every task above ticked; Re-run /launch-gaps and /launch-verdict; score has not dropped

## Day 3: Polish: Security, Payments
_Raise the score; nothing here blocks launch._  about 235 min

- [ ] Fix: User input is validated on the server (should), ~45 min
- [ ] Verify: Dependencies have no known critical vulnerabilities (should), ~45 min
- [ ] Fix: Server-only keys are not exposed to the browser (should), ~45 min
- [ ] Verify: Webhook handling is idempotent (same event twice = one effect) (should), ~45 min
- [ ] Verify: Failed payment and cancellation paths exist (should), ~45 min
- [ ] Fix: Refund/cancellation policy is stated (if charging money) (should), ~10 min

Done when: Every task above ticked; Re-run /launch-gaps and /launch-verdict; score has not dropped

## Day 4: Polish: Data, Business essentials
_Raise the score; nothing here blocks launch._  about 240 min

- [ ] Fix: Users can delete their account/data (should), ~45 min
- [ ] Fix: Named first channel (should), ~45 min
- [ ] Fix: Errors are reported to a tracker (Sentry or similar) (should), ~10 min
- [ ] Fix: A health-check endpoint exists (should), ~10 min
- [ ] Fix: Automated tests exist for the critical paths (should), ~45 min
- [ ] Fix: A CI pipeline runs build/tests on every push (should), ~10 min
- [ ] Fix: A dependency lockfile is committed (should), ~10 min
- [ ] Verify: Outbound calls (APIs, AI, email) have timeouts and failure handling (should), ~45 min
- [ ] Fix: Pages have a title, description and social preview tags (should), ~10 min
- [ ] Fix: Friendly 404 and error pages (nice), ~10 min

Done when: Every task above ticked; Re-run /launch-gaps and /launch-verdict; score has not dropped

## Day 5: Go-live checks
_Everything outside the code that must be true on launch day._  about 200 min

- [ ] Domain, HTTPS and www/bare redirect work on the production host, ~30 min
- [ ] Production environment variables set in the host; no test keys in production, ~30 min
- [ ] Payments in live mode: live webhook and secret, one real purchase and refund, ~60 min
- [ ] Email domain verified (SPF, DKIM, DMARC); receipt and reset email reach an inbox, ~30 min
- [ ] Error tracking receives a test error; uptime check alerts a channel you read, ~30 min
- [ ] Spend caps and budget alerts on every paid API and the cloud account, ~20 min

Done when: Every check passes on the production host, not on your laptop

## Day 6: Rehearse
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
- Fix: robots.txt and sitemap exist (nice)
- Fix: Images have alt text (nice)
- Fix: An .env.example documents required variables (nice)
- Fix: README explains how to run and deploy (nice)

## After launch

- **Day +1**: Read every error and support message; fix what blocks a new user
- **Week 1**: Review funnel: signup to first value to payment; pick one thing to improve
- **Day 30**: Re-run /launch, compare the score, plan the next month
