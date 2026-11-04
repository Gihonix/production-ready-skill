# auth-flows (guided)
Prefer the auth provider's built-in flows (Supabase, Clerk, Auth0, NextAuth email provider) for password reset and email verification rather than hand-rolling. If custom: single-use, expiring tokens (about 1 hour), hashed in the DB, rate-limited, same response whether or not the email exists.
