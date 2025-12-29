"""WSGI config for Insecure Banking project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insecure_banking.settings")

application = get_wsgi_application()
