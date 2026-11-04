# verify-stripe-webhook (guided)
1. Read the RAW body (`await req.text()` in Next.js; `express.raw({type:'application/json'})` BEFORE json parsing; `request.get_data()` in Flask).
2. `stripe.webhooks.constructEvent(raw, sigHeader, process.env.STRIPE_WEBHOOK_SECRET)`; on failure return 400.
3. Add `STRIPE_WEBHOOK_SECRET` to `.env.example`. MANUAL: owner creates the endpoint in the Stripe dashboard and copies its secret into the host env.
4. Grant access only from verified events, never from the success redirect. Pair with `webhook-idempotency`.
