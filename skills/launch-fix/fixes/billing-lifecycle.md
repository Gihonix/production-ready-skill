# billing-lifecycle (guided)
Handle `invoice.payment_failed` (email the user, grace period, then downgrade), `customer.subscription.deleted` (revoke access at period end), `customer.subscription.updated` (plan changes), refunds/disputes. Enable the provider's customer portal so users can update cards and cancel themselves.
