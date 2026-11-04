#!/usr/bin/env python3
"""launch-roadmap: turn open launch findings into a day-by-day plan ending in Launch Day.

Stdlib only (Python 3.8+).

    python3 roadmap.py [project_dir] --days N [--hours H] [--start YYYY-MM-DD]
                       [--out launch/roadmap.json]

N is the number of days until launch, counting Launch Day itself. Days 1..N-1 are
preparation; day N is Launch Day. Reads (all optional): launch/findings.json,
launch/logic.json, launch/improve.json, launch/verdict.json. Writes launch/roadmap.json
and launch/roadmap.md. Deterministic: the same inputs give the same plan.

Scheduling rules (also in SKILL.md):
  - Launch Day is always last; with 2+ days the day before it is a rehearsal day.
  - With 4+ days the day before that is for go-live infrastructure checks.
  - Open blockers are scheduled first. A blocker is never deferred: if it does not fit,
    the plan runs over capacity and says so.
  - Should-fix and nice-to-have items that do not fit move to "after launch".
"""
import argparse
import datetime
import json
import os
import sys

MIN_BY_TIER = {"auto": 10, "guided": 45, "manual": 30}
MIN_BY_EFFORT = {"S": 30, "M": 120, "L": 300}
SEV_RANK = {"blocker": 0, "should": 1, "nice": 2}
AREA_ORDER = ["security", "payments", "data", "logic", "business", "legal", "reliability", "auth",
              "email", "operations", "seo", "accessibility", "performance", "config"]
AREA_LABEL = {"security": "Security", "payments": "Payments", "data": "Data", "logic": "Business logic",
              "business": "Business essentials", "legal": "Legal", "reliability": "Reliability",
              "auth": "Accounts", "email": "Email", "operations": "Operations", "seo": "Search",
              "accessibility": "Accessibility", "performance": "Performance", "config": "Config"}


def load(path, default=None):
    if path and os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return default


def task(tid, title, minutes, kind, severity=None, area=None, why=None, source="plan"):
    return {"id": tid, "title": title, "minutes": minutes, "kind": kind, "severity": severity,
            "area": area, "why": why, "source": source}


def open_work(ld):
    """Open findings, logic issues and business gaps as tasks, most urgent first."""
    items = []
    fdoc = load(os.path.join(ld, "findings.json"), {"findings": []})
    items += fdoc.get("findings", [])
    items += load(os.path.join(ld, "logic.json"), {"issues": []}).get("issues", [])
    for i in load(os.path.join(ld, "improve.json"), {"issues": []}).get("issues", []):
        i.setdefault("area", "business")
        items.append(i)
    tasks = []
    for f in items:
        if f.get("status") not in ("FAIL", "UNKNOWN"):
            continue
        sev = f.get("severity", "should")
        if f.get("kind") == "suggestion":
            if f.get("value") != "high":
                continue  # only the high-value suggestions earn a slot
            minutes, sev = MIN_BY_EFFORT.get(f.get("effort"), 120), "nice"
        else:
            minutes = MIN_BY_TIER.get(f.get("fix_tier"), 45)
        verb = "Verify" if f["status"] == "UNKNOWN" else "Fix"
        tasks.append(task(f["id"], "%s: %s" % (verb, f["title"]), minutes, "fix", sev,
                          f.get("area", "config"), f.get("why"), f["id"]))
    tasks.sort(key=lambda t: (SEV_RANK.get(t["severity"], 1),
                              AREA_ORDER.index(t["area"]) if t["area"] in AREA_ORDER else 99,
                              t["id"]))
    return tasks


def rehearsal_tasks():
    return [
        task("R-01", "Code freeze: only fixes for problems the rehearsal finds", 10, "gate"),
        task("R-02", "Restore last night's backup into a scratch database and open the app", 45, "check",
             why="A backup you have never restored is a hope, not a backup."),
        task("R-03", "Rollback drill: deploy a harmless change, then roll back to the previous deploy", 30, "check"),
        task("R-04", "Run the 10-minute smoke test end to end on a phone", 30, "check"),
        task("R-05", "Have 3 to 5 people sign up cold; watch where they stall, do not help", 60, "check"),
        task("R-06", "Write the announcement post and the first support-reply templates", 45, "prep"),
    ]


def infra_tasks():
    return [
        task("I-01", "Domain, HTTPS and www/bare redirect work on the production host", 30, "check"),
        task("I-02", "Production environment variables set in the host; no test keys in production", 30, "check"),
        task("I-03", "Payments in live mode: live webhook and secret, one real purchase and refund", 60, "check"),
        task("I-04", "Email domain verified (SPF, DKIM, DMARC); receipt and reset email reach an inbox", 30, "check"),
        task("I-05", "Error tracking receives a test error; uptime check alerts a channel you read", 30, "check"),
        task("I-06", "Spend caps and budget alerts on every paid API and the cloud account", 20, "check"),
    ]


def launch_day_tasks():
    return [
        task("L-01", "Go / no-go gate: blockers cleared, backup restored, someone else signed up", 20, "gate"),
        task("L-02", "Deploy to production (you press the button; nothing here deploys for you)", 20, "launch"),
        task("L-03", "Run the 10-minute smoke test on production and write down the time", 15, "check"),
        task("L-04", "Announce to the first small group, then widen (private beta, waitlist, public)", 30, "launch"),
        task("L-05", "Watch errors, signups and payments for the first hour; answer every message", 60, "watch"),
        task("L-06", "Write down day-one numbers and the three things you would change first", 20, "watch"),
    ]


AFTER_LAUNCH = [
    {"when": "Day +1", "title": "Read every error and support message; fix what blocks a new user"},
    {"when": "Week 1", "title": "Review funnel: signup to first value to payment; pick one thing to improve"},
    {"when": "Day 30", "title": "Re-run /launch, compare the score, plan the next month"},
]


def build(days, hours, start, work):
    cap = int(hours * 60)
    kinds = ["work"] * days
    kinds[-1] = "launch"
    if days >= 2:
        kinds[-2] = "rehearsal"
    if days >= 4:
        kinds[-3] = "infra"
    work_idx = [i for i, k in enumerate(kinds) if k == "work"]

    plan = [{"index": i + 1, "kind": k, "tasks": []} for i, k in enumerate(kinds)]
    plan[-1]["tasks"] = launch_day_tasks()
    if days >= 2:
        plan[-2]["tasks"] = rehearsal_tasks()
    if days >= 4:
        plan[-3]["tasks"] = infra_tasks()

    deferred, warnings = [], []
    if work_idx:
        used = {i: 0 for i in work_idx}
        for t in work:
            slot = next((i for i in work_idx if used[i] + t["minutes"] <= cap), None)
            if slot is None and t["severity"] == "blocker":
                slot = min(work_idx, key=lambda i: used[i])
                t = dict(t, over_capacity=True)
            if slot is None:
                deferred.append(t)
                continue
            plan[slot]["tasks"].append(t)
            used[slot] += t["minutes"]
    else:
        # No preparation days: blockers cannot be hidden, so they sit on the earliest day and are flagged.
        for t in work:
            if t["severity"] == "blocker":
                plan[0]["tasks"].insert(0, dict(t, at_risk=True))
            else:
                deferred.append(t)

    over = [t for d in plan for t in d["tasks"] if t.get("over_capacity") or t.get("at_risk")]
    if over:
        mins = sum(t["minutes"] for t in over)
        warnings.append("%d blocker(s), about %d min, do not fit in %d day(s) at %s h/day. Add days or hours, "
                        "or accept launching with them open." % (len(over), mins, days, hours))
    if days == 1:
        warnings.append("One day leaves no time to rehearse or roll back. Treat this as a private beta.")

    themes = {"launch": ("Launch Day", "Ship it, watch it, learn from it."),
              "rehearsal": ("Rehearse", "Break it on purpose while it is still safe."),
              "infra": ("Go-live checks", "Everything outside the code that must be true on launch day.")}
    for d in plan:
        k = d["kind"]
        if k in themes:
            d["theme"], d["goal"] = themes[k]
        else:
            tasks = d["tasks"]
            blockers = [t for t in tasks if t["severity"] == "blocker"]
            areas = []
            for t in tasks:
                lab = AREA_LABEL.get(t["area"], t["area"] or "")
                if lab and lab not in areas:
                    areas.append(lab)
            if not tasks:
                d["theme"], d["goal"] = "Buffer", "Nothing scheduled: use it to absorb overruns or start early."
            elif blockers:
                d["theme"] = "Close blockers" + (": " + ", ".join(areas[:2]) if areas else "")
                d["goal"] = "%d blocker(s) closed and re-checked." % len(blockers)
            else:
                d["theme"] = "Polish" + (": " + ", ".join(areas[:2]) if areas else "")
                d["goal"] = "Raise the score; nothing here blocks launch."
        d["minutes"] = sum(t["minutes"] for t in d["tasks"])
        d["label"] = "Launch Day" if k == "launch" else "Day %d" % d["index"]
        if start:
            d["date"] = (start + datetime.timedelta(days=d["index"] - 1)).isoformat()
        d["exit_criteria"] = {
            "work": ["Every task above ticked", "Re-run /launch-gaps and /launch-verdict; score has not dropped"],
            "infra": ["Every check passes on the production host, not on your laptop"],
            "rehearsal": ["Backup restored, rollback worked, a stranger finished signup", "Announcement text is written"],
            "launch": ["Smoke test passes on production", "You can see errors and signups as they happen"],
        }[k]
    return plan, deferred, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--days", type=int, required=True, help="days until launch, counting Launch Day")
    ap.add_argument("--hours", type=float, default=4.0, help="working hours per preparation day")
    ap.add_argument("--start", help="date of Day 1 (YYYY-MM-DD); omit for undated plan")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.days < 1 or a.days > 90:
        sys.exit("--days must be between 1 and 90")
    if a.hours <= 0 or a.hours > 16:
        sys.exit("--hours must be between 0 and 16")
    start = None
    if a.start:
        try:
            start = datetime.date.fromisoformat(a.start)
        except ValueError:
            sys.exit("--start must look like 2026-11-20")

    root = os.path.abspath(a.project)
    ld = os.path.join(root, "launch")
    work = open_work(ld)
    plan, deferred, warnings = build(a.days, a.hours, start, work)
    verdict = load(os.path.join(ld, "verdict.json"), {})
    if not verdict:
        warnings.append("No verdict.json: the plan has no audit input. Run /launch first for a real plan.")

    out = {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": a.days, "hours_per_day": a.hours, "start": a.start,
        "verdict_at_planning": verdict.get("verdict"), "readiness_at_planning": verdict.get("readiness"),
        "plan": plan, "deferred": deferred, "after_launch": AFTER_LAUNCH, "warnings": warnings,
    }
    outp = a.out or os.path.join(ld, "roadmap.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)

    md = ["# Launch roadmap", "",
          "%d day(s) to launch, %g h/day of preparation." % (a.days, a.hours)]
    if verdict:
        md.append("Planned from verdict **%s** (readiness %s)." % (verdict.get("verdict"), verdict.get("readiness")))
    md.append("")
    for w in warnings:
        md.append("> **Heads up:** " + w)
    if warnings:
        md.append("")
    for d in plan:
        title = "## %s%s: %s" % (d["label"], " (%s)" % d["date"] if d.get("date") else "", d["theme"])
        md += [title, "_%s_  about %d min" % (d["goal"], d["minutes"]), ""]
        for t in d["tasks"]:
            flag = " **[over capacity]**" if t.get("over_capacity") else (" **[at risk]**" if t.get("at_risk") else "")
            sev = " (%s)" % t["severity"] if t.get("severity") else ""
            md.append("- [ ] %s%s, ~%d min%s" % (t["title"], sev, t["minutes"], flag))
        md += ["", "Done when: " + "; ".join(d["exit_criteria"]), ""]
    if deferred:
        md += ["## Moved to after launch", ""] + ["- %s (%s)" % (t["title"], t["severity"]) for t in deferred] + [""]
    md += ["## After launch", ""] + ["- **%s**: %s" % (x["when"], x["title"]) for x in AFTER_LAUNCH] + [""]
    with open(os.path.join(os.path.dirname(outp), "roadmap.md"), "w") as f:
        f.write("\n".join(md))
    print("roadmap: %d day(s), %d scheduled task(s), %d deferred, %d warning(s)" % (
        a.days, sum(len(d["tasks"]) for d in plan), len(deferred), len(warnings)))


if __name__ == "__main__":
    main()
