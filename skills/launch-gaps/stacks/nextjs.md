# Next.js extra checks (add as STK-NEXT-nn findings)

- Server Actions and route handlers are public endpoints. Each must check the session and ownership, like any API route.
- `middleware.ts` matcher: confirm it covers `/api/*` and private pages; a matcher that skips `/api` leaves them open.
- Anything in `NEXT_PUBLIC_*` is shipped to every browser. No service-role keys, no secrets.
- Webhook routes need the raw body: `await req.text()` before verifying, not `req.json()`.
- `next.config.js`: `headers()` for security headers; `images.remotePatterns` not set to `**`.
- Env vars needed at build time are set in the host, not only in a local `.env.local`.
- `generateMetadata` / `metadata` present on the main pages; `app/not-found.tsx` and `app/error.tsx` exist.
- Dynamic routes that read a record by id must also check the record belongs to the caller.
