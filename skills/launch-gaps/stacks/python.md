# Python (FastAPI / Flask / Django) extra checks (STK-PY-nn)

- Django: `DEBUG=False`, `ALLOWED_HOSTS` set, `SECRET_KEY` from env, `SECURE_*` and `CSRF` settings, `python manage.py check --deploy` output read.
- Flask: `app.run(debug=True)` never in production; use gunicorn/uwsgi; `SECRET_KEY` from env; CSRF on forms.
- FastAPI: auth via `Depends(...)` on every non-public route; Pydantic models for bodies; CORS allow-list; docs (`/docs`) restricted or off in production if the API is private.
- Parameterised queries or ORM; no f-string SQL.
- Pinned dependencies (lockfile); `pip-audit` clean of criticals.
- Background work (Celery/RQ) has retries and a way to see failures.
