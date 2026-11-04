# Business essentials catalog

Each item is a thing a launched product should be able to point at. Default severity
shown; context (money, personal data, business customers) can raise it. Mark `NA` only
when the item truly does not apply, and say why.

## Clarity: can a stranger understand it?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-01 | One-sentence promise | should | The first screen says what it does and for whom without jargon |
| BIZ-02 | Named target customer | should | README or copy names who it is for and the problem solved |
| BIZ-03 | A clear next step | should | The first screen has one primary action (try, sign up, join) |
| BIZ-04 | Proof it works | nice | Demo, screenshots, numbers, testimonial or a public repo with real usage |

## Money: can it earn and stay alive?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-05 | A price or an explicit "free" | blocker if taking money, else should | Pricing is visible and matches checkout, or the project states it is free and how it is funded |
| BIZ-06 | Price covers cost to serve | blocker if paid APIs, else should | `pricing.json` or an estimate shows contribution above zero at expected usage |
| BIZ-07 | Refund and cancellation terms | blocker if taking money | Written, linked from pricing and checkout |
| BIZ-08 | Receipts and billing contact | should if taking money | Buyer gets a receipt and knows who to ask about a charge |

## Trust: will they hand over data and money?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-09 | A real operator behind it | should | Name or company, contact address, and a place to write to |
| BIZ-10 | Privacy and data handling in plain words | blocker if personal data | States what is collected, who receives it (including AI providers) and how to delete it |
| BIZ-11 | Terms of use | should | Exists and is linked; for businesses, says what the owner is and is not responsible for |

## Learning: will you know if it fails?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-12 | One success metric and one way to measure it | should | A named number (signups, activated users, paid) that analytics or the database can produce |
| BIZ-13 | A way for users to reach you | blocker if taking money, else should | Working support address or form, and an owner who reads it |
| BIZ-14 | A feedback loop | nice | In-app feedback, an exit or cancel question, or a scheduled call with first users |

## Growth: will anyone arrive?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-15 | Named first channel | should | One specific place the first 20 users come from, not "social media" |
| BIZ-16 | Reason to return or share | nice | An email sequence, saved work, shareable output or referral |
| BIZ-17 | Found by name | nice | A search for the product name finds it: title tag, description, social card |

## Continuity: can it survive a bad week?

| Id | Essential | Default | Passes when |
| --- | --- | --- | --- |
| BIZ-18 | Someone who can act when it breaks | should | An owner and a backup way to reach them; access to hosting, domain and payments is not on one person's laptop alone |
| BIZ-19 | What happens to users if you stop | nice | Export, notice period or open-source fallback stated |

## Logical gap cross-checks (LOGIC-nn)

Not catalog items: found by comparing parts of the project. Number them in the order
found. Default severity `should`; `blocker` when the mismatch loses money (price
below cost, a paywalled promise given away) or misleads buyers about what they get.
