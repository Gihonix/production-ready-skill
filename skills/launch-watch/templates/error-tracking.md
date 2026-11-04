# Error tracking starter (Sentry shown; any tracker works)

- DSN comes from env: `SENTRY_DSN` (never commit it). Add `SENTRY_DSN=` to `.env.example`.
- Next.js: `npx @sentry/wizard@latest -i nextjs`. Node: `Sentry.init({ dsn: process.env.SENTRY_DSN, environment: process.env.NODE_ENV, tracesSampleRate: 0.1, sendDefaultPii: false })`. Python: `sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], traces_sample_rate=0.1, send_default_pii=False)`.
- Test once after deploy: throw a deliberate error from a hidden route, confirm it appears, then delete the route.
- Alert rule: email/Slack on every NEW issue; digest for recurring ones.
