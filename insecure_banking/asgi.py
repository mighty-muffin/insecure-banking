"""ASGI config for Insecure Banking project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insecure_banking.settings")

application = get_asgi_application()
