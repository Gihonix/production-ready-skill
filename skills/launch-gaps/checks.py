#!/usr/bin/env python3
"""launch-gaps: mechanical launch-readiness checks.

Stdlib only (Python 3.8+). Read-only on the project; writes one JSON file.

    python3 checks.py [project_dir] [--inventory launch/inventory.json]
                      [--context '{"takes_money":true,"personal_data":true}']
                      [--out launch/findings.json]
    python3 checks.py --catalog > checklist.md      # regenerate the human checklist

Statuses: PASS | FAIL | UNKNOWN | NA.  A finding with needs_confirm=true is a
heuristic result: the skill MUST read the cited code and then set the final
status (or leave UNKNOWN). Secret VALUES are never written: only file, line, type.

To add a check: add a dict to CATALOG and (if mechanical) a function to CHECKS.
"""
import argparse
import json
import os
import re
import sys

# ----------------------------------------------------------------------------
# Catalog: single source of truth for the checklist.
#   fix_tier: auto | guided | manual      fix_id: recipe name in launch-fix/fixes/
# ----------------------------------------------------------------------------
def C(id, area, severity, title, why, fix_tier, fix_id, verify, mech=True):
    return dict(id=id, area=area, severity=severity, title=title, why=why,
                fix_tier=fix_tier, fix_id=fix_id, verify=verify, mechanical=mech)


CATALOG = [
    C("SEC-01", "security", "blocker", "No .env file committed to the repo",
      "Anyone with repo access (or a leak) gets your real keys and can run up your bills or read your data.",
      "guided", "untrack-env", "List tracked env files; rotate any keys that were committed."),
    C("SEC-02", "security", "should", ".gitignore excludes .env files",
      "Without it, the next `git add .` commits your secrets.", "auto", "gitignore-env", ".gitignore contains .env*"),
    C("SEC-03", "security", "blocker", "No secrets hard-coded in source",
      "Keys in code end up in git history and, for frontend code, in every visitor's browser.",
      "guided", "move-secrets-to-env", "Grep for key patterns; rotate anything found."),
    C("SEC-04", "security", "blocker", "Every API route that changes or reveals user data checks who is calling",
      "An unprotected route lets anyone on the internet read or edit other users' data.",
      "guided", "protect-routes", "Read each flagged route; confirm it verifies a session/token and the owner of the record.", ),
    C("SEC-05", "security", "should", "Rate limiting on login, signup and expensive routes",
      "Bots can brute-force passwords, spam you, or burn paid API credits within hours of launch.",
      "auto", "rate-limit", "Look for a rate-limit library or provider setting."),
    C("SEC-06", "security", "should", "Security headers set (CSP/HSTS/X-Frame-Options etc.)",
      "Cheap protection against clickjacking, MIME sniffing and some XSS.", "auto", "security-headers", "helmet / headers() / middleware"),
    C("SEC-07", "security", "should", "CORS is not open to every origin",
      "A wildcard CORS policy lets any website call your API from your users' browsers.", "auto", "tighten-cors", "origin '*' / allow_origins ['*']"),
    C("SEC-08", "security", "blocker", "Debug mode is off for production",
      "Debug mode exposes stack traces, internal paths and sometimes an interactive console.", "auto", "disable-debug", "DEBUG=True / debug=True"),
    C("SEC-09", "security", "should", "User input is validated on the server",
      "Without validation, malformed or hostile input reaches your database and crashes things.", "guided", "validate-input", "zod/joi/pydantic/etc. used on API inputs"),
    C("SEC-10", "security", "blocker", "Database access rules (row-level security) are enabled",
      "With Supabase/Firebase, the browser talks to the database directly: no rules means anyone can read everything.",
      "guided", "enable-rls", "RLS enabled + policies per table (also check the provider dashboard)."),
    C("SEC-11", "security", "should", "Dependencies have no known critical vulnerabilities",
      "Old packages are the most common way small apps get hacked.", "guided", "audit-deps", "Run npm audit / pip-audit / equivalent and read the result.", mech=False),
    C("SEC-12", "security", "should", "Server-only keys are not exposed to the browser",
      "Variables prefixed NEXT_PUBLIC_/VITE_/REACT_APP_ are shipped to every visitor.", "guided", "move-secrets-to-env", "Look for secret-looking names in public env vars."),
    C("PAY-01", "payments", "blocker", "Payment webhooks verify the signature",
      "Without it anyone can POST a fake 'payment succeeded' and get your product free.", "guided", "verify-stripe-webhook", "constructEvent / construct_event in the webhook handler."),
    C("PAY-02", "payments", "should", "Webhook handling is idempotent (same event twice = one effect)",
      "Payment providers retry; duplicates can double-grant credits or double-send emails.", "guided", "webhook-idempotency", "Event ids stored/checked before acting.", mech=False),
    C("PAY-03", "payments", "blocker", "Paid features are enforced on the server, not only hidden in the UI",
      "Hiding a button is not access control: free users can call the API directly.", "guided", "enforce-plan-limits", "Read paid-feature routes for a plan/subscription check.", mech=False),
    C("PAY-04", "payments", "should", "Failed payment and cancellation paths exist",
      "Cards fail and customers cancel every week. Without handling, access and billing drift apart.", "guided", "billing-lifecycle", "Handlers for invoice.payment_failed / subscription.deleted.", mech=False),
    C("PAY-05", "payments", "blocker", "Live-mode keys and webhook secret configured for production (not test keys)",
      "Test keys in production mean you take no real money; live keys in dev risk real charges.", "manual", "payments-live-mode", "Check hosting env vars and provider dashboard.", mech=False),
    C("DATA-01", "data", "blocker", "Automatic database backups are on and a restore was tried",
      "One bad migration or deleted table can end the business without a backup you've actually restored.", "manual", "enable-backups", "Provider dashboard: backups/PITR.", mech=False),
    C("DATA-02", "data", "should", "Database schema changes are tracked as migrations",
      "Hand-edited production databases drift and can't be rebuilt or rolled back.", "guided", "add-migrations", "migrations dir / prisma migrate / alembic / supabase/migrations"),
    C("DATA-03", "data", "should", "Users can delete their account/data",
      "Privacy laws (GDPR/CCPA) expect it, and users ask within weeks.", "guided", "account-deletion", "Search for delete-account flow."),
    C("REL-01", "reliability", "should", "Errors are reported to a tracker (Sentry or similar)",
      "Without it you learn about crashes from angry users, if at all.", "auto", "error-tracking", "sentry in dependencies/config"),
    C("REL-02", "reliability", "should", "A health-check endpoint exists",
      "Uptime monitors and hosts need one URL that says 'I'm alive'.", "auto", "health-endpoint", "/health, /api/health, /healthz, /ping"),
    C("REL-03", "reliability", "should", "Automated tests exist for the critical paths",
      "Without tests, every AI edit after launch can silently break signup or payment.", "guided", "add-smoke-tests", "tests dir / test runner"),
    C("REL-04", "reliability", "should", "A CI pipeline runs build/tests on every push",
      "Catches broken builds before users do.", "auto", "add-ci", ".github/workflows or equivalent"),
    C("REL-05", "reliability", "should", "A dependency lockfile is committed",
      "Without it, production can install different versions than you tested.", "auto", "add-lockfile", "package-lock.json / pnpm-lock.yaml / poetry.lock etc."),
    C("REL-06", "reliability", "nice", "Friendly 404 and error pages",
      "A raw stack trace or blank page at launch looks broken and leaks details.", "auto", "error-pages", "not-found / error.tsx / 404.html"),
    C("REL-07", "reliability", "should", "Outbound calls (APIs, AI, email) have timeouts and failure handling",
      "One slow third party can hang every request or crash the server.", "guided", "timeouts", "Read the code around external calls.", mech=False),
    C("LEG-01", "legal", "should", "Privacy policy page exists",
      "Required in most places once you collect emails or use analytics; payment/ad providers require it.", "auto", "legal-pages", "page matching /privacy"),
    C("LEG-02", "legal", "should", "Terms of service page exists",
      "Sets the rules for use, refunds and liability; expected by payment providers.", "auto", "legal-pages", "page matching /terms"),
    C("LEG-03", "legal", "should", "Cookie/analytics consent where required",
      "Analytics or ad cookies without consent can breach EU/UK rules.", "guided", "cookie-consent", "analytics present vs consent banner."),
    C("LEG-04", "legal", "should", "Refund/cancellation policy is stated (if charging money)",
      "Disputes and chargebacks follow when buyers can't find the rules.", "auto", "legal-pages", "refund policy page or section"),
    C("SEO-01", "seo", "should", "Pages have a title, description and social preview tags",
      "This is what Google and link previews show; blank means nobody clicks.", "auto", "meta-tags", "metadata / <title> / og: tags"),
    C("SEO-02", "seo", "nice", "robots.txt and sitemap exist",
      "Helps search engines find and index the right pages.", "auto", "robots-sitemap", "robots.txt, sitemap.xml/ts"),
    C("A11Y-01", "accessibility", "nice", "Images have alt text",
      "Screen-reader users and SEO both rely on it.", "auto", "alt-text", "<img> without alt"),
    C("PERF-01", "performance", "nice", "No oversized images/assets shipped",
      "A multi-megabyte image makes the first visit slow on mobile.", "guided", "optimize-assets", "files >1MB in public/static/assets"),
    C("CFG-01", "config", "nice", "An .env.example documents required variables",
      "The next person (or you in 3 months) can't deploy without guessing.", "auto", "env-example", ".env.example present and complete"),
    C("CFG-02", "config", "nice", "README explains how to run and deploy",
      "Future you and any helper need it.", "auto", "readme", "README.md present with run steps"),
    C("AUTH-01", "auth", "should", "Password reset and email verification work (or a managed provider handles them)",
      "Users who forget a password become support tickets or lost customers; unverified emails enable abuse.", "guided", "auth-flows", "Provider (Clerk/Auth0/Supabase) or custom reset flow.", mech=False),
    C("EMAIL-01", "email", "should", "Sending domain has SPF, DKIM and DMARC",
      "Otherwise your signup and receipt emails land in spam.", "manual", "email-dns", "DNS records for the sending domain.", mech=False),
    C("OPS-01", "operations", "should", "You can roll back a bad deploy",
      "The first bad release will happen; you need a way back in minutes.", "manual", "rollback", "Host rollback feature / tagged releases.", mech=False),
]
BY_ID = {c["id"]: c for c in CATALOG}

# ----------------------------------------------------------------------------
SKIP_DIRS = {".git", "node_modules", ".next", ".nuxt", "dist", "build", "out", ".venv", "venv", "env",
             "__pycache__", ".turbo", ".cache", "coverage", "target", "vendor", "launch", ".svelte-kit"}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".php", ".vue", ".svelte",
            ".astro", ".html", ".json", ".toml", ".yml", ".yaml", ".sql", ".prisma", ".md", ".mdx", ".sh"}

SECRET_PATTERNS = [
    ("Stripe live secret key", re.compile(r"sk_live_[0-9a-zA-Z]{16,}")),
    ("Stripe restricted key", re.compile(r"rk_live_[0-9a-zA-Z]{16,}")),
    ("Stripe test secret key", re.compile(r"sk_test_[0-9a-zA-Z]{16,}")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("OpenAI-style key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("JWT (possible service-role key)", re.compile(r"\beyJ[A-Za-z0-9_-]{15,}\.eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}")),
    ("Hard-coded credential assignment", re.compile(
        r"""(?i)\b(?:api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*['"][A-Za-z0-9_\-/+=]{20,}['"]""")),
]
PUBLIC_SECRETISH = re.compile(r"(?:NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_|PUBLIC_)\w*(?:SECRET|SERVICE_ROLE|PRIVATE|PASSWORD)\w*")


def load(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            yield p, os.path.relpath(p, root).replace(os.sep, "/")


class Ctx(object):
    def __init__(self, root, inv, context):
        self.root, self.inv, self.context = root, inv, context
        self.files = {}      # rel -> text, for code files
        self.sizes = []      # (rel, bytes)
        self.all_rel = []
        for p, rel in walk(root):
            self.all_rel.append(rel)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            self.sizes.append((rel, sz))
            base = os.path.basename(p)
            if base.startswith(".env"):
                continue
            if os.path.splitext(p)[1].lower() in CODE_EXT and sz < 800_000:
                self.files[rel] = load(p)
        self.services = set(s["name"] for s in inv.get("services", []))

    def grep(self, pattern, exts=None, flags=re.I, limit=10, skip_tests=True):
        rx = re.compile(pattern, flags)
        hits = []
        for rel, t in self.files.items():
            if exts and os.path.splitext(rel)[1].lower() not in exts:
                continue
            if skip_tests and re.search(r"(^|/)(tests?|__tests__|spec|fixtures)/|\.(test|spec)\.", rel):
                continue
            for m in rx.finditer(t):
                hits.append({"file": rel, "line": t.count("\n", 0, m.start()) + 1})
                break
            if len(hits) >= limit:
                break
        return hits

    def has_dep(self, *names):
        blob = " ".join(t for r, t in self.files.items()
                        if os.path.basename(r) in ("package.json", "requirements.txt", "pyproject.toml", "Pipfile", "Gemfile", "go.mod", "composer.json")).lower()
        return any(n.lower() in blob for n in names)

    def exists(self, *patterns):
        return [r for r in self.all_rel if any(re.search(p, r, re.I) for p in patterns)]

    @property
    def takes_money(self):
        return bool(self.context.get("takes_money")) or bool(self.services & {"stripe", "paypal", "lemonsqueezy", "paddle", "razorpay"})

    @property
    def personal_data(self):
        return self.context.get("personal_data", True) or bool(self.services & {"clerk", "auth0", "next-auth", "supabase", "firebase"})

    @property
    def web_frontend(self):
        s = set(self.inv.get("stack", []))
        return bool(s & {"next", "react", "vue", "svelte", "nuxt", "astro", "remix", "vite"}) or bool(self.exists(r"\.html$", r"templates/"))


def R(status, evidence=None, note=None, confirm=False, severity=None):
    return dict(status=status, evidence=evidence or [], note=note, needs_confirm=confirm, severity=severity)


# ----------------------------------------------------------------------------
# Mechanical checks. Each returns R(...).
# ----------------------------------------------------------------------------
def c_sec01(x):
    f = x.inv.get("env_files_committed", [])
    return R("FAIL", [{"file": p, "line": 1} for p in f], "Env file(s) are not git-ignored; if ever committed, rotate every key inside.") if f else R("PASS")


def c_sec02(x):
    return R("PASS") if x.inv.get("gitignore_covers_env") else R(
        "FAIL", [{"file": ".gitignore", "line": 1}], ".gitignore does not list .env files.")


def c_sec03(x):
    ev = []
    for rel, t in x.files.items():
        if re.search(r"(^|/)(tests?|__tests__|fixtures|examples?)/|\.(test|spec)\.|\.md$|\.mdx$|lock\.json$|\.lock$|\.example$", rel):
            continue
        for name, rx in SECRET_PATTERNS:
            m = rx.search(t)
            if m:
                ev.append({"file": rel, "line": t.count("\n", 0, m.start()) + 1, "type": name})
                break
    if not ev:
        return R("PASS", note="No known key patterns found (patterns only; not a guarantee).")
    only_test = all("test" in e["type"].lower() for e in ev)
    return R("FAIL", ev[:15], "Values are hidden on purpose: open the file and line, move the value to an env var, then rotate the key.",
             confirm=True, severity="should" if only_test else None)


def c_sec04(x):
    routes = [r for r in x.inv.get("routes", []) if r.get("methods") != ["GET"] or True]
    if not routes:
        return R("NA", note="No API routes detected.")
    public = re.compile(r"(health|ping|webhook|login|signin|signup|register|auth|callback|public|status|version|robots|sitemap|og|csrf|logout|ready|metrics|docs|openapi)", re.I)
    cand = [r for r in routes if r.get("auth") is False and not public.search(r["path"])]
    if cand:
        ev = [{"file": r["file"], "line": r["line"], "route": "%s %s" % ("/".join(r["methods"]), r["path"])} for r in cand[:15]]
        if x.inv.get("middleware"):
            return R("UNKNOWN", ev, "Routes show no auth check in-file, but a middleware exists: confirm its matcher covers them.", confirm=True)
        return R("FAIL", ev, "%d route(s) show no sign of an auth check. Confirm by reading each." % len(cand), confirm=True)
    if any(r.get("auth") is None for r in routes):
        return R("UNKNOWN", note="Some routes (e.g. Django urls) can't be judged by pattern.", confirm=True)
    return R("PASS", note="Auth-related code found near every route. That proves presence, not correctness: spot-check ownership checks.", confirm=True)


def c_sec05(x):
    if not x.inv.get("routes") and not x.web_frontend:
        return R("NA")
    h = x.grep(r"ratelimit|rate[-_ ]limit|express-rate-limit|slowapi|flask-limiter|@upstash/ratelimit|throttle|limiter")
    return R("PASS", h[:3]) if h else R("FAIL", note="No rate-limiting code or library found. If your host/CDN (Cloudflare, Vercel firewall) rate-limits for you, mark PASS and say where.", confirm=True)


def c_sec06(x):
    if not x.web_frontend and not x.inv.get("routes"):
        return R("NA")
    h = x.grep(r"helmet|Content-Security-Policy|Strict-Transport-Security|X-Frame-Options|secure_headers|SecurityMiddleware|talisman")
    return R("PASS", h[:3]) if h else R("FAIL", note="No security-header setup found (host-level headers in vercel.json/netlify.toml count: check).", confirm=True)


def c_sec07(x):
    h = x.grep(r"""origin\s*:\s*['"]\*['"]|allow_origins\s*=\s*\[\s*['"]\*['"]|Access-Control-Allow-Origin['"]?\s*[:,]\s*['"]\*|CORS_ALLOW_ALL_ORIGINS\s*=\s*True|cors\(\s*\)""")
    return R("FAIL", h, "CORS allows any origin.", confirm=True) if h else R("PASS")


def c_sec08(x):
    h = x.grep(r"^\s*DEBUG\s*=\s*True|app\.run\([^)]*debug\s*=\s*True|debug\s*:\s*true|uvicorn\.run\([^)]*reload\s*=\s*True", flags=re.M | re.I)
    h = [e for e in h if not e["file"].endswith((".md", ".mdx"))]
    return R("FAIL", h, "Debug/reload mode appears enabled. Fine in dev; make sure production overrides it.", confirm=True) if h else R("PASS")


def c_sec09(x):
    if not x.inv.get("routes"):
        return R("NA")
    return R("PASS", note="Validation library present in dependencies.", confirm=True) if x.has_dep("zod", "joi", "yup", "valibot", "pydantic", "express-validator", "class-validator", "marshmallow", "ajv", "djangorestframework") else R(
        "FAIL", note="No validation library found; check whether routes validate input by hand.", confirm=True)


def c_sec10(x):
    if not (x.services & {"supabase", "firebase"}):
        return R("NA", note="No Supabase/Firebase detected.")
    if "supabase" in x.services:
        sql = [r for r in x.files if r.endswith(".sql")]
        rls = x.grep(r"enable\s+row\s+level\s+security", exts={".sql"})
        if rls:
            pol = x.grep(r"create\s+policy", exts={".sql"})
            return R("PASS", rls[:3], note=None if pol else "RLS enabled but no policies found: tables will be unreadable or, worse, misconfigured.", confirm=True)
        if sql:
            return R("FAIL", [{"file": sql[0], "line": 1}], "SQL files exist but none enable row level security.", confirm=True)
        return R("UNKNOWN", note="No SQL migrations in the repo: open the Supabase dashboard > Authentication > Policies and confirm every table has RLS on.")
    rules = x.exists(r"firestore\.rules$", r"database\.rules\.json$", r"storage\.rules$")
    if rules:
        txt = " ".join(x.files.get(r, "") for r in rules)
        if re.search(r"allow\s+(read|write)[^;]*:\s*if\s+true", txt):
            return R("FAIL", [{"file": rules[0], "line": 1}], "Firebase rules allow everyone ('if true').", confirm=True)
        return R("PASS", [{"file": rules[0], "line": 1}], "Rules file present: read it to confirm it limits access per user.", confirm=True)
    return R("UNKNOWN", note="No Firebase rules file in the repo: check the Firebase console.")


def c_sec12(x):
    h = x.grep(PUBLIC_SECRETISH.pattern, flags=0)
    return R("FAIL", h, "A server-style secret is exposed through a public (browser) env variable.", confirm=True) if h else R("PASS")


def webhook_files(x):
    return [r for r, t in x.files.items() if re.search(r"webhook", r, re.I) or re.search(r"stripe[-_.]signature|webhooks?\.construct", t, re.I)]


def c_pay01(x):
    if not (x.services & {"stripe", "paddle", "lemonsqueezy", "razorpay", "paypal"}):
        return R("NA", note="No payment provider detected.")
    wf = [r for r in webhook_files(x) if r.endswith((".ts", ".tsx", ".js", ".py", ".mjs", ".rb", ".go", ".php"))]
    if not wf:
        return R("UNKNOWN", note="Payment provider found but no webhook handler in the repo: how do you learn a payment succeeded? If only via the redirect URL, buyers can fake it.", confirm=True)
    verify = re.compile(r"constructEvent|construct_event|webhooks\.construct|verifyHeader|verify_signature|signature|hmac|X-Signature", re.I)
    bad = [r for r in wf if not verify.search(x.files[r])]
    if bad:
        return R("FAIL", [{"file": r, "line": 1} for r in bad], "Webhook handler has no signature verification.", confirm=True)
    return R("PASS", [{"file": r, "line": 1} for r in wf[:3]], "Signature verification present; confirm it uses the RAW request body.", confirm=True)


def c_data02(x):
    if not (x.inv.get("models") or x.services & {"postgres", "mysql", "prisma", "supabase", "sqlalchemy", "mongodb"}):
        return R("NA", note="No database detected.")
    m = x.exists(r"(^|/)migrations?/", r"prisma/migrations", r"alembic/", r"drizzle/", r"supabase/migrations")
    return R("PASS", [{"file": m[0], "line": 1}]) if m else R("FAIL", note="No migrations folder: schema lives only in your live database.", confirm=True)


def c_data03(x):
    if not x.personal_data:
        return R("NA")
    h = x.grep(r"delete[-_ ]?(account|user|me)|deleteUser|account/delete|admin\.deleteUser|remove[-_ ]account")
    return R("PASS", h[:3], confirm=True) if h else R("FAIL", note="No delete-account flow found.", confirm=True)


def c_rel01(x):
    return R("PASS") if "sentry" in x.services or x.has_dep("sentry", "bugsnag", "rollbar", "honeybadger", "highlight.run", "@logtail", "datadog") else R("FAIL", note="No error-tracking SDK found.")


def c_rel02(x):
    if not x.inv.get("routes") and not x.inv.get("deploy"):
        return R("NA")
    r = [q for q in x.inv.get("routes", []) if re.search(r"health|ping|ready|alive|status", q["path"], re.I)]
    return R("PASS", [{"file": r[0]["file"], "line": r[0]["line"]}]) if r else R("FAIL", note="No /health-style route detected.")


def c_rel03(x):
    t = x.inv.get("tests", [])
    only_dep = all("(test runner in deps)" in s or "(pytest)" in s for s in t)
    if not t:
        return R("FAIL", note="No test files or runner found.")
    if only_dep:
        return R("FAIL", note="A test runner is installed but no test files were found.")
    return R("PASS", [{"file": t[0], "line": 1}], "Tests exist; whether they cover signup/payment is a judgment call.", confirm=True)


def c_rel04(x):
    return R("PASS", [{"file": x.inv["ci"][0], "line": 1}]) if x.inv.get("ci") else R("FAIL", note="No .github/workflows. (GitLab/CircleCI users: mark PASS with the file.)", confirm=True)


def c_rel05(x):
    return R("PASS") if x.inv.get("lockfiles") else (R("NA") if not x.has_dep("name", "dependencies", "django", "flask", "fastapi") else R("FAIL"))


def c_rel06(x):
    if not x.web_frontend:
        return R("NA")
    h = x.exists(r"(^|/)(not-found|error|404|500|global-error)\.(tsx|jsx|js|ts|html|vue|svelte)$", r"templates/(404|500)\.html")
    return R("PASS", [{"file": h[0], "line": 1}]) if h else R("FAIL", note="No custom 404/error page found.")


def c_leg01(x):
    if not x.personal_data and not x.web_frontend:
        return R("NA")
    h = [p for p in x.inv.get("legal_pages", []) if re.search(r"privacy", p, re.I)] or [r for r in x.exists(r"privacy") if r.endswith((".tsx", ".jsx", ".html", ".md", ".mdx", ".vue", ".svelte", ".astro"))]
    sev = "blocker" if (x.personal_data and (x.takes_money or x.services & {"clerk", "auth0", "next-auth", "supabase", "firebase", "posthog", "google-analytics"})) else None
    return R("PASS", [{"file": h[0], "line": 1}]) if h else R("FAIL", note="No privacy-policy page found. Template only; have a professional review.", severity=sev)


def c_leg02(x):
    if not x.web_frontend:
        return R("NA")
    h = [p for p in x.inv.get("legal_pages", []) if re.search(r"terms|tos", p, re.I)] or x.exists(r"terms")
    return R("PASS", [{"file": h[0], "line": 1}]) if h else R("FAIL", note="No terms page found.", severity="blocker" if x.takes_money else None)


def c_leg03(x):
    an = x.services & {"google-analytics", "posthog", "plausible"}
    if not an:
        return R("NA", note="No analytics/ad trackers detected.")
    if "plausible" in an and len(an) == 1:
        return R("NA", note="Plausible is cookieless; consent is usually not needed.")
    h = x.grep(r"cookie[-_ ]?(consent|banner)|react-cookie-consent|cookiebot|onetrust|iubenda|termly")
    return R("PASS", h[:2]) if h else R("FAIL", note="Analytics present but no consent mechanism found.", confirm=True)


def c_leg04(x):
    if not x.takes_money:
        return R("NA")
    h = x.exists(r"refund|cancel")
    h = [r for r in h if r.endswith((".tsx", ".jsx", ".html", ".md", ".mdx", ".vue", ".svelte", ".astro"))] or x.grep(r"refund polic|refunds? (are|will|within)|money[- ]back")
    return R("PASS", [{"file": h[0] if isinstance(h[0], str) else h[0]["file"], "line": 1}]) if h else R("FAIL", note="No refund/cancellation policy found.", confirm=True)


def c_seo01(x):
    if not x.web_frontend:
        return R("NA")
    d = x.grep(r"""name=["']description["']|description\s*:\s*["'`]|metadata\s*[:=]|generateMetadata|<Head|useHead|<title""")
    og = x.grep(r"og:title|openGraph|og:image|twitter:card")
    if d and og:
        return R("PASS", d[:2])
    return R("FAIL", note="Missing: %s." % ", ".join(n for n, v in (("title/description", d), ("Open Graph/social tags", og)) if not v), confirm=True)


def c_seo02(x):
    if not x.web_frontend:
        return R("NA")
    r = x.exists(r"(^|/)robots\.(txt|ts|js)$")
    s = x.exists(r"(^|/)sitemap[^/]*\.(xml|ts|js)$")
    return R("PASS", [{"file": (r or s)[0], "line": 1}]) if (r and s) else R("FAIL", note="Missing: %s." % ", ".join(n for n, v in (("robots.txt", r), ("sitemap", s)) if not v))


def c_a11y01(x):
    ev = []
    rx = re.compile(r"<img(?![^>]*\balt\s*=)[^>]*>", re.I)
    for rel, t in x.files.items():
        if rel.endswith((".tsx", ".jsx", ".html", ".vue", ".svelte", ".astro")):
            m = rx.search(t)
            if m:
                ev.append({"file": rel, "line": t.count("\n", 0, m.start()) + 1})
    return R("FAIL", ev[:10], "%d file(s) have <img> without alt." % len(ev)) if ev else R("PASS")


def c_perf01(x):
    big = [(r, s) for r, s in x.sizes if s > 1_000_000 and re.search(r"(^|/)(public|static|assets|images|img|media)/", r) and re.search(r"\.(png|jpe?g|gif|webp|svg|mp4|mov|bmp|tiff?)$", r, re.I)]
    return R("FAIL", [{"file": r, "line": 1, "bytes": s} for r, s in big[:10]], "Compress/resize these before launch.") if big else R("PASS")


def c_cfg01(x):
    if not x.inv.get("env_vars"):
        return R("NA")
    if not x.inv.get("env_example"):
        return R("FAIL", note="Code reads %d env var(s) but no .env.example documents them." % len(x.inv["env_vars"]))
    ex = ""
    for n in (".env.example", ".env.sample", ".env.template"):
        ex += load(os.path.join(x.root, n))
    names = set(re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=", ex, re.M))
    missing = [v["name"] for v in x.inv["env_vars"] if v["name"] not in names and v["name"] not in ("NODE_ENV", "PORT", "CI", "VERCEL_URL", "VERCEL", "NEXT_RUNTIME", "PWD", "HOME", "PATH")]
    return R("FAIL", note="Not in .env.example: " + ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else "")) if missing else R("PASS")


def c_cfg02(x):
    r = [d for d in x.inv.get("docs", []) if d.lower().endswith("readme.md")]
    if not r:
        return R("FAIL", note="No README.")
    t = x.files.get(r[0], "")
    return R("PASS", [{"file": r[0], "line": 1}]) if re.search(r"(?i)install|run|start|deploy|npm|pip|setup", t) else R("FAIL", [{"file": r[0], "line": 1}], "README has no run/deploy instructions.")


CHECKS = {
    "SEC-01": c_sec01, "SEC-02": c_sec02, "SEC-03": c_sec03, "SEC-04": c_sec04, "SEC-05": c_sec05,
    "SEC-06": c_sec06, "SEC-07": c_sec07, "SEC-08": c_sec08, "SEC-09": c_sec09, "SEC-10": c_sec10,
    "SEC-12": c_sec12, "PAY-01": c_pay01, "DATA-02": c_data02, "DATA-03": c_data03,
    "REL-01": c_rel01, "REL-02": c_rel02, "REL-03": c_rel03, "REL-04": c_rel04, "REL-05": c_rel05,
    "REL-06": c_rel06, "LEG-01": c_leg01, "LEG-02": c_leg02, "LEG-03": c_leg03, "LEG-04": c_leg04,
    "SEO-01": c_seo01, "SEO-02": c_seo02, "A11Y-01": c_a11y01, "PERF-01": c_perf01,
    "CFG-01": c_cfg01, "CFG-02": c_cfg02,
}

# Non-mechanical items that only apply when payments exist
PAYMENT_ONLY = {"PAY-02", "PAY-03", "PAY-04", "PAY-05"}


def catalog_markdown():
    out = ["# Launch checklist", "",
           "Generated from `CATALOG` in `checks.py`. Do not edit by hand; add items there.", ""]
    areas = []
    for c in CATALOG:
        if c["area"] not in areas:
            areas.append(c["area"])
    for a in areas:
        out += ["## " + a.capitalize(), "", "| ID | Severity | Check | Why it matters | Fix | How to verify |", "| --- | --- | --- | --- | --- | --- |"]
        for c in CATALOG:
            if c["area"] == a:
                out.append("| %s | %s | %s | %s | %s | %s |" % (c["id"], c["severity"], c["title"], c["why"], c["fix_tier"], c["verify"]))
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--inventory")
    ap.add_argument("--context", default="{}")
    ap.add_argument("--out")
    ap.add_argument("--catalog", action="store_true")
    a = ap.parse_args()
    if a.catalog:
        print(catalog_markdown())
        return 0
    root = os.path.abspath(a.project)
    inv_path = a.inventory or os.path.join(root, "launch", "inventory.json")
    if not os.path.isfile(inv_path):
        sys.exit("inventory not found at %s: run launch-scan first" % inv_path)
    with open(inv_path) as f:
        inv = json.load(f)
    try:
        context = json.loads(a.context)
    except ValueError:
        sys.exit("--context must be JSON")
    x = Ctx(root, inv, context)
    findings = []
    for c in CATALOG:
        f = dict((k, c[k]) for k in ("id", "area", "severity", "title", "why", "fix_tier", "fix_id", "verify"))
        if c["id"] in PAYMENT_ONLY and not x.takes_money:
            r = R("NA", note="Not charging money.")
        elif c["id"] in CHECKS:
            r = CHECKS[c["id"]](x)
        else:
            r = R("UNKNOWN", note="Cannot be judged from code alone: " + c["verify"], confirm=True)
        if r.get("severity"):
            f["severity"] = r["severity"]
        f.update(status=r["status"], evidence=r["evidence"], note=r["note"], needs_confirm=r["needs_confirm"])
        findings.append(f)
    out = a.out or os.path.join(root, "launch", "findings.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        json.dump({"context": context, "findings": findings}, fh, indent=2)
    cnt = {}
    for f in findings:
        cnt[f["status"]] = cnt.get(f["status"], 0) + 1
    print("wrote %s  %s" % (out, json.dumps(cnt)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
