# protect-routes (guided)
For each flagged route: (a) require a session/token, return 401 if absent; (b) when it touches a record, check the record's owner equals the caller, return 403/404 otherwise; (c) never trust a user id sent by the client, derive it from the session.
Prefer one shared helper (`requireUser()`) over repeating logic. For Next.js also check `middleware.ts` matcher covers `/api/*`. Deliberately public routes (health, webhooks with signature checks, login) stay public: list them in a comment.
Show the diff per route; add a test that an unauthenticated call gets 401 if the project has tests.
