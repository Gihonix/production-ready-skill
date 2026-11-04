# security-headers (auto)
Add: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (or CSP `frame-ancestors`), `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`. Start CSP in report-only if the app loads third-party scripts, so nothing breaks silently.
Express `helmet()`; Next.js `headers()` in next.config; Django `SecurityMiddleware` settings; otherwise host config (vercel.json / netlify.toml).
