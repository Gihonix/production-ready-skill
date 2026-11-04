# Alert rules to start with (tune after week one)

1. Site down (2 failed uptime checks) → immediate, phone.
2. New error type in production → within minutes, chat/email.
3. Error rate over 5x the last 7-day average for 10 min → immediate.
4. Payment webhook failing (provider dashboard / failed events) → immediate.
5. Failed payment rate over 5% in a day → same day.
6. API/AI spend over 2x daily forecast, or at 80% of the monthly cap → immediate; set a hard cap too.
7. Database at 80% of plan storage/connections → same day.
8. No successful backup in 24 h → same day.
9. 20+ signups from one IP/range in an hour → investigate (bots).

Every alert needs an owner and a first action written next to it. Delete alerts nobody acts on.
