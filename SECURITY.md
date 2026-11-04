# Security policy

This tool reads people's code and reports weaknesses, so we take its own security seriously.

## Report a vulnerability
Please **do not open a public issue**. Use GitHub's private reporting: Security tab → "Report a vulnerability" (https://github.com/Gihonix/production-ready-skill/security/advisories/new). Include what you found, how to reproduce it, and the impact.

We aim to acknowledge within 5 working days and to tell you what we plan to do within 14.

## What counts
- Scripts that leak secret values into output, files or logs.
- Scripts that write outside `launch/` or run arbitrary commands from project content.
- `launch-fix` instructions that could cause destructive actions without approval.
- Report pages (`report.html`) that could run injected content from a scanned project.

## What doesn't
Missed or false findings are bugs, not vulnerabilities: use the "Wrong result" issue form. This pack is a decision aid, not a penetration test or certification.
