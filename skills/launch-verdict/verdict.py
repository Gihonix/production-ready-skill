#!/usr/bin/env python3
"""launch-verdict: compute the go/no-go verdict from findings. Never hand-written.

Stdlib only (Python 3.8+).

    python3 verdict.py [project_dir] [--findings launch/findings.json]
                       [--logic launch/logic.json] [--improve launch/improve.json]
                       [--out launch/verdict.json]
                       [--no-history]

Rules (also documented in SKILL.md):
  weight:   blocker=5  should=2  nice=1        (NA findings are ignored)
  PASS earns full weight. FAIL and UNKNOWN earn nothing. UNKNOWN also lowers *confidence*.
  Ready   = no blocker FAIL, no blocker UNKNOWN, readiness >= 80
  Almost  = (blocker FAIL + blocker UNKNOWN) <= 3, or no blockers but readiness < 80
  Not yet = more than 3 open blockers
"""
import argparse
import datetime
import json
import os
import sys

W = {"blocker": 5, "should": 2, "nice": 1}
MIN_FIX = {"auto": 10, "guided": 45, "manual": 30}
AREA_ORDER = ["security", "payments", "data", "logic", "business", "legal", "reliability", "auth", "email", "operations",
              "seo", "accessibility", "performance", "config"]


def load(p, default=None):
    if p and os.path.isfile(p):
        with open(p) as f:
            return json.load(f)
    return default


def score(items):
    tot = earn = ver = 0
    for f in items:
        if f["status"] == "NA":
            continue
        w = W.get(f["severity"], 1)
        tot += w
        if f["status"] == "PASS":
            earn += w
        if f["status"] in ("PASS", "FAIL"):
            ver += w
    if tot == 0:
        return None, None
    return round(100.0 * earn / tot), round(100.0 * ver / tot)


def minutes_label(m):
    if m < 60:
        return "about %d min" % m
    return "about %.1f h" % (m / 60.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--findings")
    ap.add_argument("--logic")
    ap.add_argument("--improve")
    ap.add_argument("--out")
    ap.add_argument("--no-history", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.project)
    ld = os.path.join(root, "launch")
    fdoc = load(a.findings or os.path.join(ld, "findings.json"))
    if not fdoc:
        sys.exit("findings.json not found: run launch-gaps first")
    items = list(fdoc["findings"])
    logic = load(a.logic or os.path.join(ld, "logic.json"), {"issues": []})
    for i in logic.get("issues", []):
        i.setdefault("area", "logic")
        i.setdefault("fix_tier", "guided")
        items.append(i)
    improve = load(a.improve or os.path.join(ld, "improve.json"), {"issues": []})
    for i in improve.get("issues", []):
        if i.get("kind", "gap") != "gap":
            continue  # suggestions never move the verdict; only enforced gaps do
        i.setdefault("area", "business")
        i.setdefault("fix_tier", "manual")
        items.append(i)

    open_items = [f for f in items if f["status"] in ("FAIL", "UNKNOWN")]
    blockers = [f for f in open_items if f["severity"] == "blocker"]
    b_fail = [f for f in blockers if f["status"] == "FAIL"]
    b_unk = [f for f in blockers if f["status"] == "UNKNOWN"]
    overall, confidence = score(items)
    if overall is None:
        overall, confidence = 0, 0

    areas = {}
    for ar in AREA_ORDER + sorted(set(f["area"] for f in items) - set(AREA_ORDER)):
        sub = [f for f in items if f["area"] == ar and f["status"] != "NA"]
        if not sub:
            continue
        s, c = score(sub)
        areas[ar] = {"score": s, "confidence": c,
                     "pass": sum(1 for f in sub if f["status"] == "PASS"),
                     "fail": sum(1 for f in sub if f["status"] == "FAIL"),
                     "unknown": sum(1 for f in sub if f["status"] == "UNKNOWN")}

    n_block = len(blockers)
    if n_block == 0 and overall >= 80:
        verdict = "Ready"
    elif n_block <= 3:
        verdict = "Almost"
    else:
        verdict = "Not yet"

    def rank(f):
        ar = AREA_ORDER.index(f["area"]) if f["area"] in AREA_ORDER else 99
        return (-W.get(f["severity"], 1), 0 if f["status"] == "FAIL" else 1, ar, MIN_FIX.get(f.get("fix_tier"), 45))

    top = sorted(open_items, key=rank)[:5]
    fix_min = sum(MIN_FIX.get(f.get("fix_tier"), 45) for f in blockers)

    risky_areas = set(f["area"] for f in blockers)
    if verdict == "Ready":
        soft = "Yes. Open it to real users, starting small and watching the first day (see launch-watch)."
    elif risky_areas & {"security", "payments", "data"}:
        soft = ("Not with real users' data or money yet. Open blockers in %s could expose data or lose money. "
                "Fix those first, then a small private beta is reasonable." % ", ".join(sorted(risky_areas & {"security", "payments", "data"})))
    else:
        soft = "A small private beta (friends, under ~20 people) is reasonable now; fix the blockers before going public."

    out = {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict, "readiness": overall, "confidence": confidence,
        "blockers_open": n_block, "blockers_failing": len(b_fail), "blockers_unverified": len(b_unk),
        "open_total": len(open_items), "passed": sum(1 for f in items if f["status"] == "PASS"),
        "estimated_blocker_fix_minutes": fix_min,
        "areas": areas, "top_fixes": [{"id": f["id"], "title": f["title"], "severity": f["severity"], "status": f["status"],
                                       "fix_tier": f.get("fix_tier"), "why": f.get("why")} for f in top],
        "soft_launch": soft,
        "unconfirmed_heuristics": sum(1 for f in items if f.get("needs_confirm") and f["status"] in ("FAIL", "PASS")),
    }
    outp = a.out or os.path.join(ld, "verdict.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)

    if not a.no_history:
        hp = os.path.join(ld, "history.json")
        hist = load(hp, [])
        hist.append({"ts": out["generated"], "readiness": overall, "confidence": confidence,
                     "verdict": verdict, "blockers": n_block})
        with open(hp, "w") as f:
            json.dump(hist[-100:], f, indent=2)

    md = ["# Launch verdict: **%s**" % verdict, "",
          "Readiness **%d/100** · Confidence **%d/100** (how much was verified rather than guessed) · Open blockers **%d**" % (overall, confidence, n_block), ""]
    if n_block:
        md.append("Fixing the blockers: %s of work (rough estimate)." % minutes_label(fix_min))
        md.append("")
    md += ["**Safe to soft-launch?** " + soft, "", "## Top fixes", ""]
    for i, f in enumerate(top, 1):
        md.append("%d. **%s** `%s` (%s, %s): %s" % (i, f["title"], f["id"], f["severity"], f["status"].lower(), f.get("why", "")))
    if not top:
        md.append("Nothing open.")
    md += ["", "## By area", "", "| Area | Score | Confidence | Pass | Fail | Unknown |", "| --- | --- | --- | --- | --- | --- |"]
    for ar, v in areas.items():
        md.append("| %s | %s | %s | %d | %d | %d |" % (ar, v["score"], v["confidence"], v["pass"], v["fail"], v["unknown"]))
    md += ["", "_Computed by verdict.py from findings.json. Rules: blockers weigh 5, should 2, nice 1; UNKNOWN counts as not passed. Ready needs zero open blockers and readiness 80+._", ""]
    with open(os.path.join(os.path.dirname(outp), "verdict.md"), "w") as f:
        f.write("\n".join(md))
    print("%s  readiness=%d confidence=%d blockers=%d" % (verdict, overall, confidence, n_block))
    return 0


if __name__ == "__main__":
    sys.exit(main())
