# Node / Express extra checks (STK-NODE-nn)

- `app.use(helmet())`, `express-rate-limit` on auth routes, `cors({origin: [...]})` with an allow-list.
- `express.json({limit})` set; body-size limits on uploads.
- Central error handler that does not leak stack traces when `NODE_ENV=production`.
- `NODE_ENV=production` set on the host; session cookies `httpOnly`, `secure`, `sameSite`.
- Passwords hashed with bcrypt/argon2, never stored or logged in plain text.
- Raw-body parser for webhook routes registered BEFORE `express.json()`.
- Graceful handling of unhandled promise rejections; process manager or host restarts on crash.
- No `eval`, no string-built SQL: use parameterised queries.
