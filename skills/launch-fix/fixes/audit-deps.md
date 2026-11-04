# audit-deps (guided)
Run `npm audit --omit=dev` / `pnpm audit` / `pip-audit` / `bundle audit` if available. Report counts by severity and the top criticals, not the whole dump. Upgrade patch/minor fixes; for majors, ask first and run build + tests after. Do not run `npm audit fix --force` without approval.
