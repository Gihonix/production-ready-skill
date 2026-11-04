# Supabase extra checks (STK-SUPA-nn)

- RLS enabled on EVERY table in `public`, with policies that tie rows to `auth.uid()`. A table with RLS on and no policy is locked; RLS off is open to the world through the anon key.
- The `service_role` key is server-only. If it appears in client code or a `NEXT_PUBLIC_` variable, treat it as leaked and rotate it.
- Storage buckets: public only if intended; policies on `storage.objects`.
- Auth: email confirmation on, redirect URLs limited to your domains, password rules set, SMTP configured (the default sender is heavily rate-limited).
- Database: backups on (PITR on paid plans), migrations committed in `supabase/migrations`.
- Edge functions verify the JWT unless deliberately public (webhooks verify their own signature).
