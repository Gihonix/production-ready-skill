# rollback (manual)
Owner steps: know the host's "promote previous deployment" button (Vercel/Netlify/Render/Fly releases) and test it once; tag releases in git (`git tag v1.0.0`); keep database migrations backward-compatible for one release so code can roll back; write the 3-step rollback in `launch/runbook.md`.
