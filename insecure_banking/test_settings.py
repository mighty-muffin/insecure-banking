"""Test-specific Django settings configuration."""

from insecure_banking.settings import *

# Override settings for testing
DEBUG = False

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# Cache configuration for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable template caching
for template in TEMPLATES:
    template.setdefault("OPTIONS", {})
    template["OPTIONS"]["debug"] = True

# Disable whitenoise during tests if installed
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Speed up tests by using simpler serializers
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Allow all hosts in tests
ALLOWED_HOSTS = ["*", "testserver"]
