# error-tracking (auto)
Add Sentry (or the owner's choice): `npx @sentry/wizard@latest -i nextjs` or the SDK init for the stack, DSN from env `SENTRY_DSN`, release tag from the commit, `tracesSampleRate` low. Strip PII (`sendDefaultPii: false`). Add `SENTRY_DSN=` to `.env.example`. MANUAL: owner creates the project and sets the DSN. See `launch-watch/templates/`.
