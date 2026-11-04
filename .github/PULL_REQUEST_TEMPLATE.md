## What this changes

## Checklist
- [ ] `python3 tests/run_tests.py` passes
- [ ] New check: entry in `CATALOG`, a fix recipe in `skills/launch-fix/fixes/`, a planted flaw in `tests/fixtures.py` and an assertion in `tests/run_tests.py`
- [ ] Regenerated the checklist: `python3 skills/launch-gaps/checks.py --catalog > skills/launch-gaps/checklist.md`
- [ ] Standard library only, Python 3.8 compatible, no network calls in scripts
- [ ] No secret values or personal data anywhere (fixture secrets are assembled at test time)
- [ ] A failing item cites evidence; unverifiable items are UNKNOWN, never PASS
