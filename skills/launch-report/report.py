#!/usr/bin/env python3
"""launch-report: render launch/report.html, one offline, self-contained page.

Stdlib only (Python 3.8+). No network requests, no CDN. Reads whatever exists in launch/:
  inventory.json  findings.json  verdict.json  history.json  logic.json  pricing.json  checklist.json

    python3 report.py [project_dir] [--out launch/report.html]

logic.json   : {"issues":[finding-like...], "journey":[{"step":"Sign up","status":"ok|weak|missing","note":""}]}
pricing.json : {"currency":"$","period":"month","your_price":19,"competitors":[{"name":"X","price":29,"url":"https://..."}],
                "tiers":[{"name":"Free","price":0,"includes":"..."}], "break_even_users":8}
checklist.json: {"groups":[{"title":"Launch day","items":["Domain points to prod", ...]}]}
"""
import argparse
import html
import json
import math
import os
import sys

E = html.escape


def load(p, d=None):
    if os.path.isfile(p):
        try:
            with open(p) as f:
                return json.load(f)
        except ValueError:
            return d
    return d


def gauge(score, label, cls):
    r, c = 70, 2 * math.pi * 70
    off = c * (1 - max(0, min(100, score)) / 100.0)
    return ('<svg viewBox="0 0 180 180" class="gauge" role="img" aria-label="Readiness %d out of 100">'
            '<circle cx="90" cy="90" r="70" class="g-track"/>'
            '<circle cx="90" cy="90" r="70" class="g-fill %s" stroke-dasharray="%.1f" stroke-dashoffset="%.1f" transform="rotate(-90 90 90)"/>'
            '<text x="90" y="92" class="g-num">%d</text><text x="90" y="116" class="g-lbl">%s</text></svg>') % (score, cls, c, off, score, E(label))


def radar(areas):
    names = list(areas.keys())
    n = len(names)
    if n < 3:
        return ""
    cx = cy = 150
    R = 100
    pts, labels, rings = [], [], []
    for k in (25, 50, 75, 100):
        rp = []
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            rp.append("%.1f,%.1f" % (cx + R * k / 100.0 * math.cos(ang), cy + R * k / 100.0 * math.sin(ang)))
        rings.append('<polygon points="%s" class="ring"/>' % " ".join(rp))
    for i, nm in enumerate(names):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        s = areas[nm]["score"] or 0
        pts.append("%.1f,%.1f" % (cx + R * s / 100.0 * math.cos(ang), cy + R * s / 100.0 * math.sin(ang)))
        lx, ly = cx + (R + 22) * math.cos(ang), cy + (R + 22) * math.sin(ang)
        anchor = "middle" if abs(math.cos(ang)) < 0.3 else ("start" if math.cos(ang) > 0 else "end")
        labels.append('<text x="%.1f" y="%.1f" text-anchor="%s" class="rl">%s</text>' % (lx, ly + 4, anchor, E(nm)))
        rings.append('<line x1="%d" y1="%d" x2="%.1f" y2="%.1f" class="ring"/>' % (cx, cy, cx + R * math.cos(ang), cy + R * math.sin(ang)))
    return ('<svg viewBox="-50 0 400 300" class="radar" role="img" aria-label="Scores by area">%s'
            '<polygon points="%s" class="rpoly"/>%s</svg>') % ("".join(rings), " ".join(pts), "".join(labels))


def history_chart(hist):
    if len(hist) < 2:
        return '<p class="muted">Run the pack again after fixing things: your score history will appear here.</p>'
    w, h, pad = 520, 140, 24
    xs = [pad + i * (w - 2 * pad) / (len(hist) - 1.0) for i in range(len(hist))]
    ys = [h - pad - (e["readiness"] / 100.0) * (h - 2 * pad) for e in hist]
    pts = " ".join("%.1f,%.1f" % p for p in zip(xs, ys))
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="4" class="dot"><title>%s: %d</title></circle>' % (x, y, E(e["verdict"]), e["readiness"]) for x, y, e in zip(xs, ys, hist))
    return ('<svg viewBox="0 0 %d %d" class="hist" role="img" aria-label="Readiness over time">'
            '<line x1="%d" y1="%d" x2="%d" y2="%d" class="ring"/><line x1="%d" y1="%d" x2="%d" y2="%d" class="ring"/>'
            '<polyline points="%s" class="line"/>%s'
            '<text x="%d" y="%d" class="rl">0</text><text x="%d" y="%d" class="rl">100</text></svg>') % (
        w, h, pad, h - pad, w - pad, h - pad, pad, pad, w - pad, pad, pts, dots, 4, h - pad + 4, 0, pad + 4)


def arch_map(inv, findings):
    flagged = {}
    for f in findings:
        if f["status"] == "FAIL":
            for e in f.get("evidence", []):
                flagged.setdefault(e["file"], []).append(f["id"])
    cols = [
        ("Pages", [(p["path"], p["file"]) for p in inv.get("pages", [])][:14]),
        ("API routes", [("%s %s" % ("/".join(r["methods"]), r["path"]), r["file"]) for r in inv.get("routes", [])][:16]),
        ("Data", [(m["name"], m["file"]) for m in inv.get("models", [])][:14]),
        ("Services", [(s["name"], s["file"]) for s in inv.get("services", [])][:14]),
    ]
    out = ['<div class="arch">']
    for title, items in cols:
        out.append('<div class="col"><h4>%s <span class="muted">%d</span></h4>' % (E(title), len(items)))
        if not items:
            out.append('<div class="node none">none found</div>')
        for label, file_ in items:
            ids = flagged.get(file_, [])
            out.append('<div class="node%s" title="%s">%s%s</div>' % (
                " bad" if ids else "", E(file_), E(label), ('<span class="tag">%s</span>' % E(", ".join(sorted(set(ids))[:3]))) if ids else ""))
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def journey(steps):
    if not steps:
        return ""
    out = ['<div class="journey">']
    for i, s in enumerate(steps):
        out.append('<div class="step %s"><b>%s</b><span>%s</span></div>' % (E(s.get("status", "ok")), E(s["step"]), E(s.get("note", ""))))
        if i < len(steps) - 1:
            out.append('<div class="arrow">→</div>')
    out.append("</div>")
    return "".join(out)


def price_chart(p):
    comp = list(p.get("competitors", []))
    cur = p.get("currency", "$")
    rows = [(c["name"], c["price"], c.get("url"), False) for c in comp]
    if p.get("your_price") is not None:
        rows.append(("You", p["your_price"], None, True))
    if not rows:
        return ""
    rows.sort(key=lambda r: r[1])
    mx = max(r[1] for r in rows) or 1
    out = ['<div class="bars">']
    for name, price, url, me in rows:
        label = E(name) if not url else '<a href="%s" rel="noopener noreferrer">%s</a>' % (E(url), E(name))
        out.append('<div class="bar-row"><span class="bn">%s</span><span class="bt"><i class="%s" style="width:%.1f%%"></i></span><span class="bv">%s%s</span></div>' % (
            label, "me" if me else "", 100.0 * price / mx, E(cur), E(("%g" % price))))
    out.append("</div>")
    if p.get("break_even_users") is not None:
        out.append('<p class="muted">At your price, break-even is <b>%s paying users</b> per %s.</p>' % (E(str(p["break_even_users"])), E(p.get("period", "month"))))
    if p.get("tiers"):
        out.append('<div class="tiers">')
        for t in p["tiers"]:
            out.append('<div class="tier"><b>%s</b><div class="tp">%s%s</div><div class="muted">%s</div></div>' % (E(t["name"]), E(cur), E("%g" % t["price"]), E(t.get("includes", ""))))
        out.append("</div>")
    return "".join(out)


CSS = """
:root{--bg:#fafaf9;--card:#fff;--ink:#1c1917;--mut:#6b6761;--line:#e7e5e4;--ok:#15803d;--warn:#b45309;--bad:#b91c1c;--acc:#2563eb;--okbg:#dcfce7;--warnbg:#fef3c7;--badbg:#fee2e2}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#13110f;--card:#1c1917;--ink:#f5f5f4;--mut:#a8a29e;--line:#2e2a27;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--acc:#60a5fa;--okbg:#14301e;--warnbg:#33260c;--badbg:#3a1414}}
:root[data-theme=dark]{--bg:#13110f;--card:#1c1917;--ink:#f5f5f4;--mut:#a8a29e;--line:#2e2a27;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--acc:#60a5fa;--okbg:#14301e;--warnbg:#33260c;--badbg:#3a1414}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px 64px}h1{font-size:22px;margin:0}h2{font-size:17px;margin:32px 0 12px}h4{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.muted{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.top{display:flex;gap:24px;align-items:center;flex-wrap:wrap}.banner{flex:1;min-width:240px}
.pill{display:inline-block;padding:4px 14px;border-radius:99px;font-weight:700;font-size:20px}
.Ready{background:var(--okbg);color:var(--ok)}.Almost{background:var(--warnbg);color:var(--warn)}.Not-yet{background:var(--badbg);color:var(--bad)}
.gauge{width:170px;height:170px}.g-track{fill:none;stroke:var(--line);stroke-width:14}.g-fill{fill:none;stroke-width:14;stroke-linecap:round}
.g-fill.Ready{stroke:var(--ok)}.g-fill.Almost{stroke:var(--warn)}.g-fill.Not-yet{stroke:var(--bad)}
.g-num{font-size:44px;font-weight:700;text-anchor:middle;fill:var(--ink)}.g-lbl{font-size:12px;text-anchor:middle;fill:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.radar{width:100%;max-width:340px;margin:auto;display:block}.ring{fill:none;stroke:var(--line);stroke-width:1}.rpoly{fill:var(--acc);fill-opacity:.25;stroke:var(--acc);stroke-width:2}.rl{font-size:10px;fill:var(--mut)}
.hist{width:100%}.line{fill:none;stroke:var(--acc);stroke-width:2}.dot{fill:var(--acc)}
table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}
.arch{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}.node{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 10px;margin-bottom:6px;font-size:13px;word-break:break-all}
.node.bad{border-color:var(--bad);background:var(--badbg)}.node.none{color:var(--mut)}.tag{display:inline-block;margin-left:6px;font-size:11px;font-weight:700;color:var(--bad)}
.journey{display:flex;gap:6px;align-items:stretch;flex-wrap:wrap}.step{flex:1;min-width:120px;border-radius:10px;padding:10px;border:1px solid var(--line);background:var(--card)}
.step b{display:block}.step span{font-size:12px;color:var(--mut)}.step.missing{border-color:var(--bad);background:var(--badbg)}.step.weak{border-color:var(--warn);background:var(--warnbg)}.step.ok{border-color:var(--ok)}.arrow{align-self:center;color:var(--mut)}
.bars{display:grid;gap:6px}.bar-row{display:grid;grid-template-columns:110px 1fr 70px;gap:8px;align-items:center;font-size:14px}.bt{background:var(--line);border-radius:6px;height:14px;overflow:hidden}.bt i{display:block;height:100%;background:var(--mut)}.bt i.me{background:var(--acc)}.bv{text-align:right}
.tiers{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:12px}.tier{border:1px solid var(--line);border-radius:10px;padding:10px}.tp{font-size:20px;font-weight:700}
.filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}.filters button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:99px;padding:4px 12px;cursor:pointer;font:inherit;font-size:13px}.filters button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.f{border:1px solid var(--line);border-left-width:4px;border-radius:8px;background:var(--card);padding:10px 12px;margin-bottom:8px}.f.blocker{border-left-color:var(--bad)}.f.should{border-left-color:var(--warn)}.f.nice{border-left-color:var(--mut)}
.f h3{margin:0;font-size:14px}.f p{margin:4px 0 0;font-size:13px;color:var(--mut)}.chips span{display:inline-block;font-size:11px;font-weight:700;border-radius:99px;padding:1px 8px;margin-right:4px;border:1px solid var(--line)}
.st-FAIL{color:var(--bad)}.st-UNKNOWN{color:var(--warn)}.st-PASS{color:var(--ok)}code{font-size:12px;background:var(--line);border-radius:4px;padding:0 4px}
.chk label{display:flex;gap:8px;padding:4px 0}.chk h3{margin:14px 0 4px;font-size:14px}
footer{margin-top:40px;font-size:12px;color:var(--mut)}@media print{.filters,.theme{display:none}body{background:#fff}}
.theme{float:right;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:4px 10px;cursor:pointer}
@media (max-width:520px){.bar-row{grid-template-columns:80px 1fr 56px}}
"""

JS = """
(function(){
var sev='all',st='all';
function apply(){document.querySelectorAll('.f').forEach(function(e){
 var ok=(sev==='all'||e.dataset.sev===sev)&&(st==='all'||e.dataset.st===st);e.style.display=ok?'':'none';});}
document.querySelectorAll('.filters button').forEach(function(b){b.addEventListener('click',function(){
 var g=b.parentNode.dataset.g;if(g==='sev')sev=b.dataset.v;else st=b.dataset.v;
 b.parentNode.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});apply();});});
var key='production-ready-skill:'+location.pathname;var saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
document.querySelectorAll('.chk input').forEach(function(i){i.checked=!!saved[i.dataset.k];i.addEventListener('change',function(){
 saved[i.dataset.k]=i.checked;try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){}});});
var t=document.querySelector('.theme');if(t)t.addEventListener('click',function(){var r=document.documentElement;
 var dark=getComputedStyle(r).getPropertyValue('--bg').trim()==='#13110f';r.setAttribute('data-theme',dark?'light':'dark');});
})();
"""


def findings_board(items):
    order = {"blocker": 0, "should": 1, "nice": 2}
    items = [f for f in items if f["status"] != "NA"]
    items.sort(key=lambda f: (order.get(f["severity"], 3), {"FAIL": 0, "UNKNOWN": 1, "PASS": 2}.get(f["status"], 3)))
    out = ['<div class="filters" data-g="sev">'
           + "".join('<button data-v="%s"%s>%s</button>' % (v, ' class="on"' if v == "all" else "", l) for v, l in (("all", "All severities"), ("blocker", "Blockers"), ("should", "Should fix"), ("nice", "Nice to have")))
           + '</div><div class="filters" data-g="st">'
           + "".join('<button data-v="%s"%s>%s</button>' % (v, ' class="on"' if v == "all" else "", l) for v, l in (("all", "All"), ("FAIL", "Failing"), ("UNKNOWN", "Unverified"), ("PASS", "Passing")))
           + "</div>"]
    for f in items:
        ev = "".join("<code>%s:%s</code> " % (E(e["file"]), E(str(e.get("line", "")))) for e in f.get("evidence", [])[:4])
        fixed = f.get("fixed")
        out.append('<div class="f %s" data-sev="%s" data-st="%s"><h3><span class="st-%s">%s</span> %s <span class="muted">%s</span></h3><p>%s</p>%s<div class="chips">%s%s</div></div>' % (
            E(f["severity"]), E(f["severity"]), E(f["status"]), E(f["status"]), E(f["status"]), E(f["title"]), E(f["id"]),
            E(f.get("why", "")), ("<p>%s%s</p>" % (ev, E(f.get("note") or ""))) if (ev or f.get("note")) else "",
            '<span>%s</span>' % E(f["severity"]),
            ('<span>fix: %s</span>' % E(f["fix_tier"]) if f.get("fix_tier") else "") + ('<span class="st-PASS">fixed</span>' if fixed else "")))
    return "".join(out)


def checklist(doc):
    out = ['<div class="card chk">']
    for g in doc.get("groups", []):
        out.append("<h3>%s</h3>" % E(g["title"]))
        for i, it in enumerate(g["items"]):
            out.append('<label><input type="checkbox" data-k="%s"> <span>%s</span></label>' % (E(g["title"] + ":" + str(i)), E(it)))
    out.append("</div>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--out")
    a = ap.parse_args()
    root = os.path.abspath(a.project)
    ld = os.path.join(root, "launch")
    inv = load(os.path.join(ld, "inventory.json"), {})
    fd = load(os.path.join(ld, "findings.json"), {"findings": []})
    vd = load(os.path.join(ld, "verdict.json"))
    if not vd:
        sys.exit("verdict.json not found: run launch-verdict first")
    hist = load(os.path.join(ld, "history.json"), [])
    logic = load(os.path.join(ld, "logic.json"), {})
    pricing = load(os.path.join(ld, "pricing.json"), {})
    chk = load(os.path.join(ld, "checklist.json"), {})
    items = list(fd["findings"]) + [dict(i, area=i.get("area", "logic")) for i in logic.get("issues", [])]
    cls = vd["verdict"].replace(" ", "-")

    body = ['<main><button class="theme" aria-label="Toggle theme">Theme</button><h1>Launch readiness: %s</h1><p class="muted">%s · generated %s</p>' % (
        E(inv.get("project", "project")), E(", ".join(inv.get("stack", [])) or "stack not detected"), E(vd["generated"]))]
    body.append('<div class="card top">%s<div class="banner"><span class="pill %s">%s</span>'
                '<p><b>Readiness %d/100</b> · confidence %d/100 · %d open blocker(s)</p><p>%s</p></div></div>' % (
                    gauge(vd["readiness"], "readiness", cls), cls, E(vd["verdict"]), vd["readiness"], vd["confidence"], vd["blockers_open"], E(vd["soft_launch"])))
    body.append("<h2>Fix these first</h2><div class='card'><ol>%s</ol></div>" % "".join(
        "<li><b>%s</b> <span class='muted'>%s · %s</span><br><span class='muted'>%s</span></li>" % (E(t["title"]), E(t["id"]), E(t["severity"]), E(t.get("why") or "")) for t in vd["top_fixes"]) or "<p>Nothing open.</p>")
    body.append('<h2>Scores by area</h2><div class="grid"><div class="card">%s</div><div class="card"><table><tr><th>Area</th><th>Score</th><th>Verified</th><th>Fail</th><th>Unknown</th></tr>%s</table></div></div>' % (
        radar(vd["areas"]), "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td></tr>" % (E(k), v["score"], v["confidence"], v["fail"], v["unknown"]) for k, v in vd["areas"].items())))
    body.append("<h2>Progress</h2><div class='card'>%s</div>" % history_chart(hist))
    if inv:
        body.append("<h2>What your app actually is</h2><p class='muted'>Red = a finding points at this file.</p>%s" % arch_map(inv, items))
    if logic.get("journey"):
        body.append("<h2>User journey</h2>%s" % journey(logic["journey"]))
    if pricing:
        body.append("<h2>Pricing vs competitors</h2><div class='card'>%s</div>" % price_chart(pricing))
    body.append("<h2>All findings</h2>%s" % findings_board(items))
    if chk.get("groups"):
        body.append("<h2>Launch and watch checklist</h2>%s" % checklist(chk))
    body.append("<footer>Generated by production-ready-skill. Raises confidence; it is not a penetration test or legal advice. Unverified items are not passes.</footer></main>")
    doc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Launch readiness</title><style>%s</style></head><body>%s<script>%s</script></body></html>' % (CSS, "".join(body), JS)
    out = a.out or os.path.join(ld, "report.html")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
