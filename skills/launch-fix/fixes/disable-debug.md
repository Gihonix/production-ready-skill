# disable-debug (auto)
Drive debug from env: `DEBUG = os.environ.get("DEBUG") == "1"`, `debug: process.env.NODE_ENV !== "production"`. Default OFF. Remove `reload=True` from production entrypoints. Make sure error responses in production do not include stack traces.
