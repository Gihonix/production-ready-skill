#!/usr/bin/env python3
"""Regenerate examples/sample-output/{before,after} by running the real pipeline on the test fixtures.

Dev-only helper: python3 scripts/make_sample.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tests"))
import fixtures  # noqa: E402

PY = sys.executable
S = lambda *p: os.path.join(REPO, "skills", *p)  # noqa: E731
CTX = '{"takes_money":true,"personal_data":true}'


def run(*a):
    subprocess.run([PY] + list(a), check=True, capture_output=True)


def extras(d):
    L = os.path.join(d, "launch")
    json.dump({"issues": [], "journey": [
        {"step": "Sign up", "status": "ok", "note": "Supabase auth"},
        {"step": "Verify email", "status": "missing", "note": "never built"},
        {"step": "Pay", "status": "weak", "note": "webhook unverified"},
        {"step": "Cancel", "status": "missing", "note": "no flow"}]}, open(os.path.join(L, "logic.json"), "w"))
    json.dump({"currency": "$", "period": "month", "your_price": 19, "break_even_users": 7,
               "competitors": [{"name": "Acme", "price": 29, "url": "https://example.com/pricing"},
                               {"name": "Beta", "price": 12, "url": "https://example.org/plans"},
                               {"name": "Gamma", "price": 49, "url": "https://example.net/pricing"}],
               "tiers": [{"name": "Free", "price": 0, "includes": "3 projects"},
                         {"name": "Pro", "price": 19, "includes": "Unlimited projects"}]}, open(os.path.join(L, "pricing.json"), "w"))
    json.dump({"groups": [{"title": "Launch day", "items": ["Domain points to production", "Stripe in live mode", "10-minute smoke test passed"]},
                          {"title": "Week one", "items": ["Check errors daily", "Review failed payments"]}]}, open(os.path.join(L, "checklist.json"), "w"))


def improve(d, state):
    """Business gaps and suggestions, as launch-improve would write them (BIZ ids and titles from essentials.md)."""
    gaps = [
        ("BIZ-07", "Refund and cancellation terms", "blocker", "Buyers who can't find the refund rules turn into chargebacks."),
        ("BIZ-13", "A way for users to reach you", "blocker", "Paying customers need a working support address and an owner who reads it."),
        ("BIZ-15", "Named first channel", "should", "Name the one place the first 20 users come from."),
    ]
    issues = [dict(id=i, kind="gap", severity=sev, status="FAIL" if state == "before" else "PASS", title=t, why=w, area="business")
              for i, t, sev, w in gaps]
    issues.append(dict(id="IMP-01", kind="suggestion", severity="nice", status="FAIL", title="Put a demo above the fold",
                       why="A 20-second demo lifts sign-ups more than any copy change.", effort="S", value="high", area="business"))
    json.dump({"issues": issues}, open(os.path.join(d, "launch", "improve.json"), "w"))


def roadmap(d, days):
    run(S("launch-roadmap/roadmap.py"), d, "--days", str(days), "--hours", "4")


def snapshot(d, name):
    out = os.path.join(REPO, "examples/sample-output", name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for n in ("report.html", "verdict.md", "verdict.json", "findings.json", "inventory.json", "history.json",
              "improve.json", "roadmap.json", "roadmap.md"):
        shutil.copy(os.path.join(d, "launch", n), out)


def main():
    tmp = tempfile.mkdtemp()
    d = os.path.join(tmp, "my-saas-app")
    try:
        fixtures.make_bad_next(d)
        run(S("launch-scan/scan.py"), d)
        run(S("launch-gaps/checks.py"), d, "--context", CTX)
        os.makedirs(os.path.join(d, "launch"), exist_ok=True)
        improve(d, "before")
        run(S("launch-verdict/verdict.py"), d)
        extras(d)
        roadmap(d, 7)
        run(S("launch-report/report.py"), d)
        snapshot(d, "before")
        # "after": same project with the planted flaws fixed, then the owner confirms the manual items
        for n in os.listdir(d):
            if n != "launch":
                p = os.path.join(d, n)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        fixtures.make_good_next(d)
        run(S("launch-scan/scan.py"), d)
        run(S("launch-gaps/checks.py"), d, "--context", CTX)
        improve(d, "after")
        run(S("launch-verdict/verdict.py"), d)  # Almost: manual blockers still unverified
        fp = os.path.join(d, "launch/findings.json")
        doc = json.load(open(fp))
        for x in doc["findings"]:
            if x["status"] == "UNKNOWN" and x["severity"] == "blocker":
                x["status"] = "PASS"
                x["note"] = "owner-confirmed"
        json.dump(doc, open(fp, "w"))
        run(S("launch-verdict/verdict.py"), d)
        extras(d)
        lg = os.path.join(d, "launch/logic.json")
        j = json.load(open(lg))
        for s in j["journey"]:
            s["status"], s["note"] = "ok", "done"
        json.dump(j, open(lg, "w"))
        roadmap(d, 3)
        run(S("launch-report/report.py"), d)
        snapshot(d, "after")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # drop the old flat sample files
    for n in os.listdir(os.path.join(REPO, "examples/sample-output")):
        p = os.path.join(REPO, "examples/sample-output", n)
        if os.path.isfile(p):
            os.remove(p)
    print("sample output written")


if __name__ == "__main__":
    main()
