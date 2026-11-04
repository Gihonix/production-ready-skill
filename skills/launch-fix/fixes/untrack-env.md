# untrack-env (guided)
Goal: stop real env files being in git, and treat their keys as exposed.
1. `git ls-files | grep -E '(^|/)\.env'` to see tracked env files.
2. `git rm --cached <file>` for each (keeps the local file). Add patterns via recipe `gitignore-env`.
3. Create/refresh `.env.example` with names only (recipe `env-example`).
4. MANUAL (always): rotate every key that was in the file. Removing it from code does not un-leak it. If the repo was ever pushed, also tell the owner history still contains it (BFG / `git filter-repo`), and that rotation is the real fix.
