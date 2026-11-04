# Incident playbook

1. **Detect**: alert, user report or dashboard. Write the time down.
2. **Assess in 5 minutes**: who is affected (everyone / some / one), is money or data at risk, did it start after a deploy?
3. **Stop the bleeding first**: roll back the last deploy; pause signups or checkout; switch off the broken feature flag; rotate a leaked key; put up a status/maintenance message. Fix properly afterwards.
4. **Communicate**: one honest message to affected users (what happened, what you did, what they should do, when you will update). Payment or data problems: do this early.
5. **Fix**: smallest safe change, run the smoke test, deploy, watch for 30 minutes.
6. **Learn**: 5 lines in `launch/incidents.md`: what happened, impact, cause, how it was detected, one change that prevents it (a test, an alert, a check).

If personal data may have been exposed: stop, preserve logs, and check what notification rules apply where your users live (ask a professional).
