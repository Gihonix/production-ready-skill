# Health endpoint templates

Rules: no auth, no secrets, fast, 200 when alive, 503 when a critical dependency is down.

**Next.js (app router)** `app/api/health/route.ts`
```ts
export const dynamic = 'force-dynamic'
export async function GET() {
  return Response.json({ ok: true, time: new Date().toISOString() })
}
```

**Express**
```js
app.get('/health', (_req, res) => res.json({ ok: true }))
```

**FastAPI**
```python
@app.get("/health")
def health():
    return {"ok": True}
```

Optional DB ping: run `select 1` with a 2 s timeout and return 503 with `{ok:false}` on failure (never include the error text).
