# enforce-plan-limits (guided)
Add one server-side helper (`requirePlan('pro')`, `assertWithinQuota(user, 'exports')`) and call it at the start of every paid or metered route. Read the plan from your own database (updated by verified webhooks), never from the client. UI hiding stays as a courtesy. Add a test: a free user calling the paid route gets 402/403.
