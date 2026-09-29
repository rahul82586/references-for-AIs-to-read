"""Root conftest — test environment defaults.

Loaded before any test module imports application code, so the fail-hard secret
checks see a configured environment. These values are test-only; production
startup refuses placeholder or missing keys (see infrastructure/config/env.py).
"""
import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-key-0123456789abcdef0123456789abcdef")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-api-key")
