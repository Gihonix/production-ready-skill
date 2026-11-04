# rate-limit (auto for in-memory, guided if a store is needed)
Apply to: login, signup, password reset, contact forms, and any route that calls a paid API.
- Express: `express-rate-limit` (per IP, e.g. 10 per minute on auth). - FastAPI: `slowapi`. - Flask: `Flask-Limiter`. - Next.js on serverless: use `@upstash/ratelimit` (needs a Redis store; ask the owner) or the host's firewall rules.
In-memory limits do not work across serverless instances: say so. Return 429 with a clear message.
