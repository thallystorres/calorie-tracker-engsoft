"""Configurações de desenvolvimento."""

from __future__ import annotations

import os

from .base import *  # noqa: F403

DEBUG = True

# Hosts padrão para dev
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
