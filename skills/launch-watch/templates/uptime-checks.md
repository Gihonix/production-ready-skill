# Uptime checks to create (any uptime tool)

| Check | URL | Interval | Alert after |
| --- | --- | --- | --- |
| Home page | https://YOUR_DOMAIN/ | 1-5 min | 2 failures |
| Health | https://YOUR_DOMAIN/health | 1 min | 2 failures |
| Login page | https://YOUR_DOMAIN/login | 5 min | 2 failures |
| API key route (expects 401 when logged out) | https://YOUR_DOMAIN/api/me | 5 min | status changes |
| Certificate expiry | YOUR_DOMAIN | daily | 30 days before |
| Domain expiry | YOUR_DOMAIN | daily | 45 days before |

Send alerts to a channel you read on your phone. Test the alert once by pausing the app.
