# Contributing

The pack is plain files: `SKILL.md` instructions plus small stdlib-only Python helpers. Keep it that way: no pip installs, Python 3.8+, works on macOS, Linux and Windows.

## Add a checklist item
1. Add an entry to `CATALOG` in `skills/launch-gaps/checks.py` (id, area, severity, title, a one-sentence plain-language *why*, fix tier, fix id, how to verify).
2. If it can be detected from files, add a function and register it in `CHECKS`. Return `FAIL` only with evidence (`file`, `line`); use `needs_confirm=True` for heuristics; use `UNKNOWN` when code can't tell.
3. Add a recipe `skills/launch-fix/fixes/<fix_id>.md` (tests enforce this).
4. Regenerate the human list: `python3 skills/launch-gaps/checks.py --catalog > skills/launch-gaps/checklist.md`.
5. Add the planted flaw to `tests/fixtures.py` and an assertion to `tests/run_tests.py`.

## Add a stack guide
Create `skills/launch-gaps/stacks/<stack>.md`: a short list of extra checks (ids `STK-<STACK>-nn`) for that stack.

## Principles
- Evidence or it didn't happen. Unverified is never PASS.
- Never print or store secret values. Fixture secrets are assembled at test time, never committed.
- Plain language first: the reader did not write the code.
- Read-only outside `launch/`; only `launch-fix` edits code, with approval.
- No network in scripts. Web research belongs in skill instructions and must cite links.

## Before a PR
`python3 tests/run_tests.py` must pass.
