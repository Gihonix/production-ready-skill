# webhook-idempotency (guided)
Create a `processed_events(event_id primary key, received_at)` table. At the start of the handler insert the event id; if it already exists return 200 without acting. Make the side effects (grant credits, send email) happen after a successful insert, ideally in one transaction. Use idempotency keys on outgoing create calls.
