# Firebase extra checks (STK-FB-nn)

- `firestore.rules` and `storage.rules` are not `allow read, write: if true`; rules check `request.auth.uid` against the document owner.
- App Check enabled for abusive-traffic protection where possible.
- Admin SDK keys / service-account JSON never in the repo or browser bundle (client config keys are fine to expose; admin keys are not).
- Budget alerts set in Google Cloud so a loop or attack can't produce a surprise bill.
- Cloud Functions validate auth and input; callable functions check `context.auth`.
