# add-smoke-tests (guided)
Add a small suite for the critical path only: the app boots, health returns 200, an unauthenticated call to a private route is rejected, sign-up works, the payment webhook rejects a bad signature. Use the project's runner (vitest/jest/pytest). Aim for 5 to 10 tests that would catch an AI edit breaking the money path.
