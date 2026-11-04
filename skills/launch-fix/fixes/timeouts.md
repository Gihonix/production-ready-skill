# timeouts (guided)
Wrap every outbound call (fetch/axios/requests, AI SDK, email) in a timeout (5 to 30 s as fits) with try/catch, a user-safe error, and logging. Retry only idempotent calls, with backoff. Never let one slow API hang the request.
