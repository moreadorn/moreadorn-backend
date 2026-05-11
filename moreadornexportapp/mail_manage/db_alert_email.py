"""Plain-text alert email sent when the database health check fails."""

from __future__ import annotations

import logging

from django.core.mail import EmailMessage

from .smtp import get_default_from_address, get_smtp_connection

logger = logging.getLogger(__name__)

ALERT_RECIPIENTS = [
    "rhydham.bhalodia122@gmail.com",
    "manavparmar43@gmail.com",
]


def send_db_inactive_alert(reason: str = "") -> bool:
    sender = get_default_from_address()
    if not sender:
        logger.warning("DB alert: no sender address configured, skipping email")
        return False

    body = (
        "Hello,\n\n"
        "This is an automated alert from the Moreadorn backend health "
        "monitor.\n\n"
        "Our scheduled health check was unable to reach the production "
        "database. The application may be unable to serve requests until "
        "connectivity is restored.\n\n"
        "Please investigate at your earliest convenience and verify that "
        "the database service is running and reachable.\n\n"
        "Regards,\n"
        "Moreadorn Monitoring"
    )
    if reason:
        body += f"\n\n---\nTechnical details:\n{reason}"

    try:
        msg = EmailMessage(
            subject="[Moreadorn] Database Inactive - Immediate Action Required",
            body=body,
            from_email=sender,
            to=ALERT_RECIPIENTS,
            connection=get_smtp_connection(),
        )
        msg.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send DB-inactive alert email")
        return False
