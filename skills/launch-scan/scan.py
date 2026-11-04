#!/usr/bin/env python3
"""launch-scan: build an inventory of what a project actually contains.

Stdlib only (Python 3.8+). Read-only on the project; writes one JSON file.

    python3 scan.py [project_dir] [--out launch/inventory.json]

Secret values are never recorded: env vars are captured by NAME only.
"""
import argparse
import fnmatch
import json
import os
import re
import sys

SKIP_DIRS = {
    ".git", "node_modules", ".next", ".nuxt", "dist", "build", "out", ".venv", "venv",
    "env", "__pycache__", ".turbo", ".cache", "coverage", ".svelte-kit", "target",
    "vendor", ".idea", ".vscode", "launch", ".expo", "Pods", ".gradle",
}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".php", ".java",
    ".vue", ".svelte", ".astro", ".json", ".toml", ".yml", ".yaml", ".sql", ".prisma",
    ".env", ".md", ".html", ".txt", ".cfg", ".ini", ".sh", ".dockerfile",
}
MAX_BYTES = 1_000_000

AUTH_TOKENS = re.compile(
    r"getServerSession|getSession|getUser\(|auth\(\)|currentUser|requireAuth|authenticate|"
    r"verifyToken|jwt\.verify|Depends\(\s*get_current|login_required|permission_classes|"
    r"IsAuthenticated|supabase\.auth|clerk|withAuth|isAuthenticated|req\.user|session\.user|"
    r"Authorization|bearer",
    re.I,
)

SERVICE_PATTERNS = {
    "stripe": r"\bstripe\b", "paypal": r"paypal", "lemonsqueezy": r"lemonsqueezy|lemon-squeezy",
    "paddle": r"\bpaddle\b", "razorpay": r"razorpay",
    "supabase": r"supabase", "firebase": r"firebase", "mongodb": r"mongoose|mongodb",
    "postgres": r"\bpg\b|postgres|psycopg|asyncpg", "mysql": r"mysql", "sqlite": r"sqlite",
    "prisma": r"prisma", "drizzle": r"drizzle", "sqlalchemy": r"sqlalchemy", "redis": r"\bredis\b|ioredis",
    "openai": r"\bopenai\b", "anthropic": r"anthropic", "gemini": r"google-generativeai|@google/genai|gemini",
    "clerk": r"@clerk|clerk", "auth0": r"auth0", "next-auth": r"next-auth|authjs|@auth/",
    "resend": r"\bresend\b", "sendgrid": r"sendgrid", "postmark": r"postmark", "mailgun": r"mailgun",
    "twilio": r"twilio", "sentry": r"sentry", "posthog": r"posthog", "plausible": r"plausible",
    "google-analytics": r"gtag|google-analytics|googletagmanager",
    "aws": r"aws-sdk|@aws-sdk|boto3", "s3": r"\bs3\b", "cloudinary": r"cloudinary",
    "uploadthing": r"uploadthing", "vercel": r"vercel", "netlify": r"netlify", "docker": r"dockerfile",
    "upstash": r"upstash", "pusher": r"pusher", "socket.io": r"socket\.io",
}
# Only check these against dependency manifests + config, to avoid false hits in prose.
DEP_ONLY = {"vercel", "netlify", "s3", "docker", "clerk"}

ENV_RE = [
    re.compile(r"process\.env\.([A-Z][A-Z0-9_]+)"),
    re.compile(r"process\.env\[['\"]([A-Z][A-Z0-9_]+)['\"]\]"),
    re.compile(r"import\.meta\.env\.([A-Z][A-Z0-9_]+)"),
    re.compile(r"os\.environ(?:\.get)?[\[\(]['\"]([A-Z][A-Z0-9_]+)['\"]"),
    re.compile(r"os\.getenv\(['\"]([A-Z][A-Z0-9_]+)['\"]"),
    re.compile(r"ENV\[['\"]([A-Z][A-Z0-9_]+)['\"]\]"),
]

EXPRESS_RE = re.compile(
    r"\b(?:app|router|server|api)\.(get|post|put|patch|delete|all)\(\s*['\"`]([^'\"`]+)['\"`]")
FASTAPI_RE = re.compile(r"@\w+\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]")
FLASK_RE = re.compile(r"@\w+\.route\(\s*['\"]([^'\"]+)['\"](?:.*methods=\[([^\]]+)\])?")
DJANGO_RE = re.compile(r"\b(?:re_)?path\(\s*r?['\"]([^'\"]*)['\"]")
MODEL_PATTERNS = [
    (re.compile(r"^model\s+(\w+)\s*\{", re.M), "prisma"),
    (re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?(?:public\.)?[\"`]?(\w+)", re.I), "sql"),
    (re.compile(r"^class\s+(\w+)\((?:[\w\.]*Model|Base|db\.Model|SQLModel)[^)]*\)", re.M), "orm"),
    (re.compile(r"mongoose\.model\(\s*['\"](\w+)['\"]"), "mongoose"),
    (re.compile(r"(?:pgTable|mysqlTable|sqliteTable)\(\s*['\"](\w+)['\"]"), "drizzle"),
]


def load_gitignore(root):
    pats = []
    p = os.path.join(root, ".gitignore")
    if os.path.isfile(p):
        with open(p, errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("!"):
                    pats.append(line.rstrip("/"))
    return pats


def ignored(name, rel, pats):
    return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel, p.lstrip("/")) for p in pats)


def walk(root):
    pats = load_gitignore(root)
    for dp, dns, fns in os.walk(root):
        rel_dir = os.path.relpath(dp, root)
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".venv")
                  and not ignored(d, os.path.normpath(os.path.join(rel_dir, d)), pats)]
        for fn in fns:
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            yield os.path.join(dp, fn), rel, ignored(fn, rel, pats)


def read(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return None


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def next_route(rel):
    """Map a Next.js file path to a URL path. Returns (kind, url) or None."""
    r = rel.replace(os.sep, "/")
    m = re.match(r"^(?:src/)?app/(.*)/?(route|page)\.(?:t|j)sx?$", r)
    if m:
        seg = [s for s in m.group(1).split("/") if s and not (s.startswith("(") and s.endswith(")"))]
        return ("api" if m.group(2) == "route" else "page", "/" + "/".join(seg))
    m = re.match(r"^(?:src/)?app/(route|page)\.(?:t|j)sx?$", r)
    if m:
        return ("api" if m.group(1) == "route" else "page", "/")
    m = re.match(r"^(?:src/)?pages/(.*)\.(?:t|j)sx?$", r)
    if m:
        p = re.sub(r"/?index$", "", m.group(1))
        if p.startswith("_"):
            return None
        return ("api" if p.startswith("api") else "page", "/" + p)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.project)
    out = a.out or os.path.join(root, "launch", "inventory.json")

    inv = {
        "project": os.path.basename(root), "root_hint": os.path.basename(root),
        "languages": {}, "stack": [], "package_manager": None, "lockfiles": [],
        "routes": [], "pages": [], "models": [], "services": [], "env_vars": [],
        "env_files_committed": [], "env_example": False, "middleware": [],
        "tests": [], "ci": [], "deploy": [], "docs": [], "legal_pages": [],
        "has_git": os.path.isdir(os.path.join(root, ".git")), "files_scanned": 0,
        "gitignore_covers_env": False,
    }
    services, env_seen = {}, {}
    deps_blob = ""
    ext_count = {}
    LANG = {".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript",
            ".tsx": "typescript", ".rb": "ruby", ".go": "go", ".php": "php", ".java": "java",
            ".vue": "vue", ".svelte": "svelte"}

    gi = os.path.join(root, ".gitignore")
    if os.path.isfile(gi):
        t = read(gi) or ""
        inv["gitignore_covers_env"] = bool(re.search(r"^\s*\.env(\*|\.local)?\s*$", t, re.M))

    for path, rel, git_ignored in walk(root):
        base = os.path.basename(path)
        ext = os.path.splitext(base)[1].lower()
        relu = rel.replace(os.sep, "/")
        inv["files_scanned"] += 1

        if base.startswith(".env"):
            if base in (".env.example", ".env.sample", ".env.template"):
                inv["env_example"] = True
            elif not git_ignored:
                inv["env_files_committed"].append(relu)
            continue  # never read env contents
        if base in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock",
                    "Pipfile.lock", "uv.lock", "Gemfile.lock", "go.sum", "composer.lock"):
            inv["lockfiles"].append(relu)
        if base == "package.json" and "node_modules" not in relu:
            t = read(path) or ""
            deps_blob += t
            try:
                pj = json.loads(t)
                alld = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
                for fw in ("next", "react", "vue", "svelte", "express", "fastify", "nestjs", "@nestjs/core",
                           "nuxt", "astro", "remix", "@remix-run/node", "vite", "hono", "koa", "expo", "electron"):
                    if fw in alld:
                        inv["stack"].append(fw)
                if any(k in alld for k in ("jest", "vitest", "mocha", "playwright", "cypress", "@playwright/test")):
                    inv["tests"].append(relu + " (test runner in deps)")
            except ValueError:
                pass
        if base in ("requirements.txt", "pyproject.toml", "Pipfile", "Gemfile", "go.mod", "composer.json"):
            deps_blob += read(path) or ""
            if base == "requirements.txt" or base == "pyproject.toml" or base == "Pipfile":
                t = (read(path) or "").lower()
                for fw in ("django", "fastapi", "flask", "streamlit", "pytest"):
                    if fw in t:
                        (inv["tests"].append(relu + " (pytest)") if fw == "pytest" else inv["stack"].append(fw))
        if relu.startswith(".github/workflows/"):
            inv["ci"].append(relu)
        if base in ("vercel.json", "netlify.toml", "fly.toml", "render.yaml", "railway.json", "railway.toml",
                    "Procfile", "app.yaml", "wrangler.toml", "Dockerfile", "docker-compose.yml", "serverless.yml"):
            inv["deploy"].append(relu)
        if re.search(r"(^|/)(test|tests|__tests__|spec|e2e)/|\.(test|spec)\.(t|j)sx?$|(^|/)test_.*\.py$", relu):
            inv["tests"].append(relu)
        if base.lower() in ("readme.md", "contributing.md", "license", "license.md"):
            inv["docs"].append(relu)
        if re.search(r"(privacy|terms|tos|cookie|refund|legal)", relu, re.I) and ext in (".tsx", ".jsx", ".html", ".md", ".vue", ".svelte", ".astro", ".mdx", ".py"):
            inv["legal_pages"].append(relu)
        if base in ("middleware.ts", "middleware.js", "middleware.py") or re.match(r"(src/)?middleware\.", relu):
            inv["middleware"].append(relu)

        if ext in LANG:
            inv["languages"][LANG[ext]] = inv["languages"].get(LANG[ext], 0) + 1
        ext_count[ext] = ext_count.get(ext, 0) + 1
        if ext not in TEXT_EXT and base not in ("Dockerfile", "Procfile"):
            continue
        text = read(path)
        if text is None:
            continue

        # Next.js file-system routes
        nr = next_route(relu)
        if nr and ext in (".ts", ".tsx", ".js", ".jsx"):
            kind, url = nr
            auth = bool(AUTH_TOKENS.search(text))
            methods = sorted(set(re.findall(r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)", text))) or (["ANY"] if kind == "api" else ["GET"])
            entry = {"path": url, "file": relu, "line": 1, "methods": methods, "auth": auth, "framework": "next"}
            (inv["routes"] if kind == "api" else inv["pages"]).append(entry)

        if ext in (".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"):
            for m in EXPRESS_RE.finditer(text):
                seg = text[m.start(): m.start() + 600]
                inv["routes"].append({"path": m.group(2), "file": relu, "line": line_of(text, m.start()),
                                      "methods": [m.group(1).upper()], "auth": bool(AUTH_TOKENS.search(seg)) or bool(AUTH_TOKENS.search(text[:m.start()][-400:])),
                                      "framework": "express"})
        if ext == ".py":
            for m in FASTAPI_RE.finditer(text):
                seg = text[m.start(): m.start() + 500]
                inv["routes"].append({"path": m.group(2), "file": relu, "line": line_of(text, m.start()),
                                      "methods": [m.group(1).upper()], "auth": bool(AUTH_TOKENS.search(seg)), "framework": "fastapi"})
            for m in FLASK_RE.finditer(text):
                seg = text[max(0, m.start() - 200): m.start() + 500]
                meth = re.findall(r"[A-Z]+", m.group(2) or "GET")
                inv["routes"].append({"path": m.group(1), "file": relu, "line": line_of(text, m.start()),
                                      "methods": meth, "auth": bool(AUTH_TOKENS.search(seg)), "framework": "flask"})
            if base == "urls.py":
                for m in DJANGO_RE.finditer(text):
                    inv["routes"].append({"path": "/" + m.group(1), "file": relu, "line": line_of(text, m.start()),
                                          "methods": ["ANY"], "auth": None, "framework": "django"})

        for rx, kind in MODEL_PATTERNS:
            for m in rx.finditer(text):
                if ext in (".md", ".txt", ".json") and kind != "prisma":
                    continue
                inv["models"].append({"name": m.group(1), "file": relu, "line": line_of(text, m.start()), "kind": kind})

        for rx in ENV_RE:
            for m in rx.finditer(text):
                env_seen.setdefault(m.group(1), (relu, line_of(text, m.start())))

        if ext in (".js", ".jsx", ".ts", ".tsx", ".py", ".mjs", ".cjs", ".vue", ".svelte", ".yml", ".yaml", ".toml", ".sql"):
            low = text
            for name, pat in SERVICE_PATTERNS.items():
                if name in DEP_ONLY:
                    continue
                m = re.search(pat, low, re.I)
                if m and name not in services:
                    services[name] = {"name": name, "file": relu, "line": line_of(text, m.start())}

    for name, pat in SERVICE_PATTERNS.items():
        if re.search(pat, deps_blob, re.I) and name not in services:
            services[name] = {"name": name, "file": "dependency manifest", "line": 0}
    # deploy files imply hosting
    for d in inv["deploy"]:
        for host in ("vercel", "netlify", "docker"):
            if host in d.lower() and host not in services:
                services[host] = {"name": host, "file": d, "line": 1}

    inv["services"] = sorted(services.values(), key=lambda s: s["name"])
    inv["env_vars"] = [{"name": k, "file": v[0], "line": v[1]} for k, v in sorted(env_seen.items())]
    inv["stack"] = sorted(set(inv["stack"]))
    inv["tests"] = sorted(set(inv["tests"]))[:40]
    # de-dup routes
    seen, routes = set(), []
    for r in inv["routes"]:
        k = (r["path"], r["file"], tuple(r["methods"]), r["line"])
        if k not in seen:
            seen.add(k)
            routes.append(r)
    inv["routes"] = routes
    inv["summary"] = {
        "routes": len(inv["routes"]), "pages": len(inv["pages"]), "models": len(inv["models"]),
        "services": len(inv["services"]), "env_vars": len(inv["env_vars"]),
        "routes_without_auth": sum(1 for r in inv["routes"] if r["auth"] is False),
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(inv, f, indent=2)
    print("scanned %d files -> %s" % (inv["files_scanned"], out))
    print(json.dumps(inv["summary"]))


if __name__ == "__main__":
    sys.exit(main())
