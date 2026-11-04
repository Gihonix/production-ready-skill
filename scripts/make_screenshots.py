#!/usr/bin/env python3
"""Regenerate the README screenshots from examples/sample-output/report.html.

Dev-only helper (needs Google Chrome and Pillow; the pack itself needs neither).
    python3 scripts/make_screenshots.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "examples/sample-output/%s/report.html")
OUT = os.path.join(REPO, "docs/img")
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

# name, source (before|after), width, sections to keep (h2 text, "__top" = header+verdict), max findings, dark
SHOTS = [
    ("verdict", "before", 1000, ["__top", "Fix these first"], None, False),
    ("scores", "before", 1000, ["Scores by area"], None, False),
    ("map", "before", 1000, ["What your app actually is"], None, False),
    ("journey-pricing", "before", 1000, ["User journey", "Pricing vs competitors"], None, False),
    ("findings", "before", 1000, ["All findings"], 5, False),
    ("roadmap", "before", 1000, ["Launch roadmap"], None, False),
    ("progress", "after", 1000, ["__top", "Progress"], None, False),
    ("verdict-dark", "before", 1000, ["__top"], None, True),
    ("mobile", "before", 390, ["__top", "Fix these first"], None, False),
]

HOOK = """
<style>.theme{display:none}%s</style>
<script>
(function(){var cfg=%s;var main=document.querySelector('main');var groups=[],cur={t:'__top',els:[]};groups.push(cur);
Array.prototype.slice.call(main.children).forEach(function(k){if(k.tagName==='H2'){cur={t:k.textContent,els:[k]};groups.push(cur);}else cur.els.push(k);});
groups.forEach(function(g){var keep=cfg.keep.indexOf(g.t)>-1;g.els.forEach(function(e){if(!keep||e.tagName==='FOOTER')e.style.display='none';});});
if(cfg.limit){Array.prototype.slice.call(document.querySelectorAll('.f')).forEach(function(e,i){if(i>=cfg.limit)e.style.display='none';});
 document.querySelectorAll('.filters').forEach(function(e){e.style.display='none'});}
})();
</script>
"""
DARK = ":root{--bg:#13110f;--card:#1c1917;--ink:#f5f5f4;--mut:#a8a29e;--line:#2e2a27;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--acc:#60a5fa;--okbg:#14301e;--warnbg:#33260c;--badbg:#3a1414}"


MAX_H = {"roadmap": 1950}  # px at 2x; the full roadmap panel is much taller than a README needs


def trim(path, bg_probe=(2, 2)):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel(bg_probe))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        pad = 24 * 2
        im = im.crop((0, 0, im.width, min(im.height, box[3] + pad)))
    cap = MAX_H.get(os.path.basename(path)[:-4])
    if cap and im.height > cap:
        im = im.crop((0, 0, im.width, cap))
    im.save(path, optimize=True)


def main():
    if not os.path.isfile(CHROME):
        sys.exit("Chrome not found; set CHROME=/path/to/chrome")
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        for name, src, width, keep, limit, dark in SHOTS:
            html = open(SRC % src).read()
            cfg = json.dumps({"keep": keep, "limit": limit})
            page = html.replace("</body>", HOOK % (DARK if dark else "", cfg) + "</body>")
            page = page.replace("<html lang=\"en\">", "<html lang=\"en\" data-theme=\"%s\">" % ("dark" if dark else "light"))
            p = os.path.join(tmp, name + ".html")
            open(p, "w").write(page)
            out = os.path.join(OUT, name + ".png")
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                            "--window-size=%d,1500" % width, "--virtual-time-budget=2000", "--screenshot=" + out, "file://" + p],
                           check=True, capture_output=True)
            trim(out)
            print("wrote", os.path.relpath(out, REPO))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
