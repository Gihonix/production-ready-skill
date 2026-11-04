#!/usr/bin/env python3
"""End-to-end tests. No dependencies: python3 tests/run_tests.py"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fixtures  # noqa: E402

PY = sys.executable
SCAN = os.path.join(REPO, "skills/launch-scan/scan.py")
CHECKS = os.path.join(REPO, "skills/launch-gaps/checks.py")
VERDICT = os.path.join(REPO, "skills/launch-verdict/verdict.py")
COST = os.path.join(REPO, "skills/launch-pricing/cost_model.py")
REPORT = os.path.join(REPO, "skills/launch-report/report.py")
ROADMAP = os.path.join(REPO, "skills/launch-roadmap/roadmap.py")
failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


def run(*args):
    r = subprocess.run([PY] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
    return r


def pipeline(d, ctx='{"takes_money":true,"personal_data":true}'):
    run(SCAN, d)
    run(CHECKS, d, "--context", ctx)
    run(VERDICT, d, "--no-history")
    with open(os.path.join(d, "launch/findings.json")) as f:
        fd = json.load(f)
    with open(os.path.join(d, "launch/verdict.json")) as f:
        vd = json.load(f)
    return {x["id"]: x for x in fd["findings"]}, vd


def structure():
    import re
    print("structure")
    sys.path.insert(0, os.path.join(REPO, "skills/launch-gaps"))
    import checks  # noqa: E402
    sdir = os.path.join(REPO, "skills")
    names = sorted(n for n in os.listdir(sdir) if os.path.isdir(os.path.join(sdir, n)))
    for n in names:
        p = os.path.join(sdir, n, "SKILL.md")
        txt = open(p).read() if os.path.isfile(p) else ""
        m = re.match(r"---\nname: (.+)\ndescription: >-\n((?:  .+\n)+)(?:argument-hint: .+\n)?---\n", txt)
        check(bool(m) and m.group(1) == n, "%s/SKILL.md has valid frontmatter and name matches folder" % n)
        check(bool(m) and len(" ".join(m.group(2).split())) < 1000, "%s description under 1000 chars" % n)
    check(len(names) == 12, "12 skills present (got %d)" % len(names))
    missing = [c["fix_id"] for c in checks.CATALOG if not os.path.isfile(os.path.join(sdir, "launch-fix/fixes", c["fix_id"] + ".md"))]
    check(not missing, "every fix_id has a recipe (missing: %s)" % sorted(set(missing)))
    ids = [c["id"] for c in checks.CATALOG]
    check(len(ids) == len(set(ids)), "catalog ids unique")
    cl = open(os.path.join(sdir, "launch-gaps/checklist.md")).read()
    check(all(i in cl for i in ids), "checklist.md is up to date with CATALOG")
    # nothing author- or machine-specific
    bad = []
    for dp, dns, fns in os.walk(REPO):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        for fn in fns:
            if fn == "run_tests.py":
                continue
            p = os.path.join(dp, fn)
            try:
                t = open(p, errors="ignore").read()
            except OSError:
                continue
            for pat in (r"/Users/", r"founder-", r"@stake\.", r"C:\\Users"):
                if re.search(pat, t):
                    bad.append("%s (%s)" % (os.path.relpath(p, REPO), pat))
    check(not bad, "no machine/author-specific references %s" % bad)


def main():
    tmp = tempfile.mkdtemp()
    try:
        print("bad fixture")
        bad = os.path.join(tmp, "bad")
        fixtures.make_bad_next(bad)
        f, v = pipeline(bad)
        for fid, file_ in (("SEC-01", ".env"), ("SEC-03", "lib/billing.ts"), ("SEC-04", "app/api/orders/route.ts"),
                           ("PAY-01", "app/api/stripe/webhook/route.ts"), ("SEC-12", "lib/db.ts")):
            ok = f[fid]["status"] == "FAIL" and any(e["file"] == file_ for e in f[fid]["evidence"])
            check(ok, "%s flagged with evidence in %s" % (fid, file_))
        check(f["SEC-01"]["severity"] == "blocker" and f["LEG-01"]["severity"] == "blocker", "legal/security severities escalate by context")
        check(v["verdict"] == "Not yet", "verdict is Not yet (got %s)" % v["verdict"])
        blob = ""
        for n in os.listdir(os.path.join(bad, "launch")):
            with open(os.path.join(bad, "launch", n)) as fh:
                blob += fh.read()
        check(fixtures.FAKE_STRIPE not in blob and fixtures.FAKE_ENV_TOKEN not in blob, "no secret values in any output")

        print("good fixture")
        good = os.path.join(tmp, "good")
        fixtures.make_good_next(good)
        f, v = pipeline(good)
        fails = [k for k, x in f.items() if x["status"] == "FAIL" and x["severity"] == "blocker"]
        check(not fails, "no blocker FAILs on fixed app (got %s)" % fails)
        check(v["verdict"] == "Almost" and v["blockers_failing"] == 0, "unverified manual blockers keep it at Almost (got %s)" % v["verdict"])
        # simulate the user confirming the manual items
        p = os.path.join(good, "launch/findings.json")
        doc = json.load(open(p))
        for x in doc["findings"]:
            if x["status"] == "UNKNOWN" and x["severity"] == "blocker":
                x["status"] = "PASS"
        json.dump(doc, open(p, "w"))
        run(VERDICT, good, "--no-history")
        v2 = json.load(open(os.path.join(good, "launch/verdict.json")))
        check(v2["verdict"] == "Ready", "verdict is Ready once blockers confirmed (got %s, readiness %s)" % (v2["verdict"], v2["readiness"]))
        check(v2["readiness"] > v["readiness"] or v["readiness"] >= 80, "readiness did not go down")

        print("other stacks")
        for name, maker, expect in (("express", fixtures.make_bad_express, ("SEC-04", "SEC-07")),
                                    ("fastapi", fixtures.make_bad_fastapi, ("SEC-04", "SEC-08"))):
            d = os.path.join(tmp, name)
            maker(d)
            f2, v2 = pipeline(d, '{}')
            for fid in expect:
                check(f2[fid]["status"] == "FAIL" and f2[fid]["evidence"], "%s: %s flagged with evidence" % (name, fid))

        structure()

        print("improve gaps and roadmap")
        imp = os.path.join(tmp, "imp")
        shutil.copytree(good, imp)
        base = json.load(open(os.path.join(imp, "launch/verdict.json")))
        json.dump({"issues": [
            {"id": "BIZ-07", "kind": "gap", "severity": "blocker", "status": "FAIL", "title": "No refund terms"},
            {"id": "IMP-01", "kind": "suggestion", "severity": "nice", "status": "FAIL", "title": "Demo above the fold",
             "effort": "S", "value": "high"}]}, open(os.path.join(imp, "launch/improve.json"), "w"))
        run(VERDICT, imp, "--no-history")
        v2 = json.load(open(os.path.join(imp, "launch/verdict.json")))
        check(v2["blockers_open"] == base["blockers_open"] + 1 and v2["verdict"] != "Ready",
              "an open BIZ blocker counts in the verdict; suggestions do not")
        check("business" in v2["areas"], "business is scored as its own area")
        if os.path.isfile(ROADMAP):
            for n in (1, 2, 3, 7):
                run(ROADMAP, imp, "--days", str(n), "--start", "2026-11-10")
                rm = json.load(open(os.path.join(imp, "launch/roadmap.json")))
                labels = [d["label"] for d in rm["plan"]]
                check(len(labels) == n and labels[-1] == "Launch Day", "%d-day roadmap ends in Launch Day" % n)
                ids = [t["id"] for d in rm["plan"] for t in d["tasks"]] + [t["id"] for t in rm["deferred"]]
                check("BIZ-07" in ids, "%d-day roadmap never drops an open blocker" % n)
                check(rm["plan"][-1]["date"] == str(datetime.date(2026, 11, 10) + datetime.timedelta(days=n - 1)),
                      "%d-day roadmap dates run to the right Launch Day" % n)
            check(run(ROADMAP, imp, "--days", "0").returncode != 0, "roadmap rejects 0 days")
            run(ROADMAP, imp, "--days", "5", "--start", "2026-11-10")
            run(REPORT, imp)
            rh = open(os.path.join(imp, "launch/report.html")).read()
            check('class="rm"' in rh and "Launch Day" in rh and "Launch in 5 days" in rh, "report renders the roadmap panel")
            check("BIZ-07" in rh, "report lists business gaps from improve.json")

        if os.path.isfile(COST):
            print("cost model")
            r = run(COST, "--price", "20", "--fixed", "100", "--variable", "3", "--fee-pct", "2.9", "--fee-fixed", "0.30", "--json")
            d = json.loads(r.stdout)
            check(abs(d["contribution_per_user"] - (20 - 3 - (20 * 0.029 + 0.30))) < 0.01, "contribution per user matches hand calc")
            check(d["break_even_users"] == 7, "break-even users = ceil(100/16.12) = 7 (got %s)" % d.get("break_even_users"))

        if os.path.isfile(REPORT):
            print("report")
            r = run(REPORT, good)
            html = open(os.path.join(good, "launch/report.html")).read()
            check("http://" not in html.replace("http://www.w3.org", "") and "https://" not in html.replace("https://www.w3.org", ""),
                  "report.html makes no network references")
            check("Ready" in html and "prefers-color-scheme" in html, "report has verdict and dark mode")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
