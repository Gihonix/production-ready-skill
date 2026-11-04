# add-ci (auto)
Create `.github/workflows/ci.yml`: on push and PR, checkout, set up the language, install from the lockfile, lint, build, test. Cache dependencies. Use the commands from the project's own scripts; if there are none, say so rather than inventing them.
