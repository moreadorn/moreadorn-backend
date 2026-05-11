"""SMTP connection helper.

Resolves the active ``EmailConfig`` row at send-time and falls back to the
``.env``-driven settings if no row is configured. Keeps ``contact_email.py``
and ``quote_email.py`` agnostic of where the credentials come from.
"""

from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.core.mail import get_connection


def _get_active_config():
    """Lazy-load the EmailConfig row to avoid AppRegistryNotReady issues
    during migrations or when this module is imported very early."""
    try:
        from ..models import EmailConfig  # local import — circular safety
    except Exception:  # pragma: no cover
        return None
    try:
        return EmailConfig.get_active()
    except Exception:  # pragma: no cover
        return None


def get_smtp_connection():
    """Return an SMTP connection.

    - If the admin has activated an ``EmailConfig`` row, use that row's
      host / port / TLS / username / password.
    - Otherwise, fall back to Django's defaults (which read ``EMAIL_HOST_*``
      from settings, i.e. ``.env``).
    """
    cfg = _get_active_config()
    if cfg and cfg.email and cfg.app_password:
        return get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=cfg.host or "smtp.gmail.com",
            port=cfg.port or 587,
            username=cfg.email,
            password=cfg.app_password,
            use_tls=bool(cfg.use_tls),
            timeout=getattr(settings, "EMAIL_TIMEOUT", 20),
        )
    return get_connection()


def get_active_from_email() -> str:
    """Return the address that emails should be sent FROM.

    Prefers the active EmailConfig's email; otherwise the configured
    EMAIL_HOST_USER from settings.
    """
    cfg = _get_active_config()
    if cfg and cfg.email:
        return cfg.email
    return settings.EMAIL_HOST_USER or ""


def get_default_from_address() -> Optional[str]:
    """Return a friendly From-header (``Moreadorn <addr>``) or None if no
    sender address is configured at all."""
    addr = get_active_from_email()
    if not addr:
        return None
    site_name = getattr(settings, "SITE_NAME", "Moreadorn")
    return f"{site_name} <{addr}>"
