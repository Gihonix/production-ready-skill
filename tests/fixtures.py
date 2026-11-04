"""Generate fixture apps at test time.

Fake secrets are assembled from fragments here so that no secret-looking string
is stored in the repository (keeps secret scanners and GitHub push protection quiet).
"""
import os

FAKE_STRIPE = "sk_" + "live_" + "A1b2C3d4E5f6G7h8I9j0K1l2"
FAKE_ENV_TOKEN = "supersecretvalue" + "1234567890"


def w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def make_bad_next(root):
    """Next.js + Supabase + Stripe app with planted flaws."""
    w(root, "package.json", '{"name":"bad-next","dependencies":{"next":"14.0.0","react":"18","stripe":"14","@supabase/supabase-js":"2"}}')
    w(root, ".env", "STRIPE_SECRET_KEY=%s\nAPP_TOKEN=%s\n" % (FAKE_STRIPE, FAKE_ENV_TOKEN))
    # no .gitignore -> SEC-02 and SEC-01
    w(root, "app/page.tsx", "export default function Home(){return <div><img src='/a.png'/>Hello</div>}\n")
    w(root, "app/api/orders/route.ts",
      "import { supabase } from '@/lib/db'\n"
      "export async function GET(req: Request){\n  const { data } = await supabase.from('orders').select('*')\n  return Response.json(data)\n}\n"
      "export async function DELETE(req: Request){\n  await supabase.from('orders').delete().neq('id', 0)\n  return Response.json({ok:true})\n}\n")
    w(root, "app/api/stripe/webhook/route.ts",
      "import Stripe from 'stripe'\n"
      "const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)\n"
      "export async function POST(req: Request){\n  const event = await req.json()\n  if(event.type==='checkout.session.completed'){ /* grant access */ }\n  return Response.json({received:true})\n}\n")
    w(root, "lib/db.ts", "import { createClient } from '@supabase/supabase-js'\n"
      "export const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!)\n")
    w(root, "lib/billing.ts", "const KEY = '%s'\n" % FAKE_STRIPE)
    w(root, "supabase/migrations/001.sql", "create table orders (id serial primary key, user_id uuid, total int);\n")
    w(root, "README.md", "# bad\n")


def make_good_next(root):
    """Same app with the planted flaws fixed."""
    make_bad_next(root)
    os.remove(os.path.join(root, ".env"))
    os.remove(os.path.join(root, "lib/billing.ts"))
    w(root, ".gitignore", ".env\n.env.local\nnode_modules\n.next\n")
    w(root, ".env.example", "STRIPE_SECRET_KEY=\nNEXT_PUBLIC_SUPABASE_URL=\nSUPABASE_SERVICE_ROLE_KEY=\nSTRIPE_WEBHOOK_SECRET=\n")
    w(root, "lib/db.ts", "import { createClient } from '@supabase/supabase-js'\n"
      "export const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)\n")
    w(root, "app/api/orders/route.ts",
      "import { getServerSession } from 'next-auth'\nimport { supabase } from '@/lib/db'\nimport { z } from 'zod'\nimport { Ratelimit } from '@upstash/ratelimit'\n"
      "export async function GET(req: Request){\n  const session = await getServerSession()\n  if(!session) return new Response('no',{status:401})\n"
      "  const { data } = await supabase.from('orders').select('*').eq('user_id', session.user.id)\n  return Response.json(data)\n}\n")
    w(root, "app/api/stripe/webhook/route.ts",
      "import Stripe from 'stripe'\n"
      "const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)\n"
      "export async function POST(req: Request){\n  const body = await req.text()\n"
      "  const event = stripe.webhooks.constructEvent(body, req.headers.get('stripe-signature')!, process.env.STRIPE_WEBHOOK_SECRET!)\n  return Response.json({received:true})\n}\n")
    w(root, "app/api/health/route.ts", "export async function GET(){return Response.json({ok:true})}\n")
    w(root, "app/privacy/page.tsx", "export default function P(){return <div>Privacy</div>}\n")
    w(root, "app/terms/page.tsx", "export default function T(){return <div>Terms</div>}\n")
    w(root, "app/refund-policy/page.tsx", "export default function T(){return <div>Refunds within 14 days</div>}\n")
    w(root, "app/not-found.tsx", "export default function N(){return <div>404</div>}\n")
    w(root, "app/robots.ts", "export default function robots(){return {rules:{userAgent:'*'}}}\n")
    w(root, "app/sitemap.ts", "export default function sitemap(){return []}\n")
    w(root, "app/layout.tsx", "export const metadata = { title: 'x', description: 'y', openGraph: { title: 'x' } }\nexport default function L({children}){return <html>{children}</html>}\n")
    w(root, "app/page.tsx", "export default function Home(){return <div><img src='/a.png' alt='logo'/>Hello</div>}\n")
    w(root, "supabase/migrations/001.sql", "create table orders (id serial primary key, user_id uuid, total int);\nalter table orders enable row level security;\ncreate policy own on orders for select using (auth.uid() = user_id);\n")
    w(root, "tests/orders.test.ts", "test('x',()=>{})\n")
    w(root, ".github/workflows/ci.yml", "name: ci\non: [push]\njobs: {}\n")
    w(root, "package-lock.json", "{}")
    w(root, "package.json", '{"name":"good-next","dependencies":{"next":"14.0.0","react":"18","stripe":"14","@supabase/supabase-js":"2","zod":"3","@sentry/nextjs":"7","@upstash/ratelimit":"1"},"devDependencies":{"vitest":"1"}}')
    w(root, "README.md", "# good\n\nRun: npm install && npm run dev. Deploy: vercel.\n")
    w(root, "next.config.js", "module.exports={async headers(){return [{source:'/(.*)',headers:[{key:'X-Frame-Options',value:'DENY'},{key:'Strict-Transport-Security',value:'max-age=1'}]}]}}\n")


def make_bad_express(root):
    w(root, "package.json", '{"name":"bad-express","dependencies":{"express":"4","pg":"8","openai":"4"}}')
    w(root, ".gitignore", "node_modules\n")
    w(root, "server.js",
      "const express = require('express')\nconst cors = require('cors')\nconst app = express()\napp.use(cors({ origin: '*' }))\n"
      "app.post('/api/chat', async (req, res) => { /* calls paid AI, no auth */ res.json({ok:true}) })\n"
      "app.get('/api/users/:id', (req, res) => res.json({}))\n"
      "app.listen(process.env.PORT || 3000)\n")


def make_bad_fastapi(root):
    w(root, "requirements.txt", "fastapi\nuvicorn\nsqlalchemy\n")
    w(root, "main.py",
      "from fastapi import FastAPI\nimport uvicorn\napp = FastAPI()\n\n"
      "@app.get('/items/{item_id}')\ndef item(item_id: int):\n    return {}\n\n"
      "@app.post('/admin/reset')\ndef reset():\n    return {}\n\n"
      "if __name__ == '__main__':\n    uvicorn.run('main:app', reload=True)\n")
