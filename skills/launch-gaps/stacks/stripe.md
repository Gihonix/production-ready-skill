# Stripe extra checks (STK-STRIPE-nn)

- Webhook endpoint verifies `Stripe-Signature` with the endpoint secret on the RAW body.
- Handle at minimum: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`.
- Idempotency: store processed `event.id`; use idempotency keys on create calls.
- Access is granted from webhook/server state, never from the success-page redirect alone.
- Prices/amounts come from server-side Price IDs, never from client-sent amounts.
- Test and live keys, webhook secrets and Price IDs are separate; production env uses `sk_live`/`whsec` for the LIVE endpoint.
- Customer portal enabled so users can update cards and cancel without emailing you.
- Tax/invoice settings reviewed for your country (not legal advice).
