# move-secrets-to-env (guided)
1. Replace the literal with `process.env.NAME` / `os.environ["NAME"]` (fail loudly at startup if missing).
2. Add `NAME=` (no value) to `.env.example`; tell the owner to set the real value in the host's env settings.
3. Public-prefixed vars (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`) must never hold secrets: rename without the prefix and read it server-side only. Service-role/admin keys live only on the server.
4. MANUAL: rotate the exposed key. Never print the value.
