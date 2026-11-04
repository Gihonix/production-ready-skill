# enable-backups (manual)
Owner steps: turn on automatic backups (Supabase: Database > Backups, PITR on paid plans; Neon/RDS/PlanetScale: retention settings; Firebase: scheduled exports; Mongo Atlas: Cloud Backup). Then do a RESTORE into a scratch project once and confirm the data is there. Write the date of the last successful restore test in `launch/runbook.md`.
