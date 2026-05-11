"""Shared DB health-check logic.

Used by both the Vercel-triggered cron view (`cron_views.DBHealthCronView`)
and the local management command (`manage.py check_db_health`) so the
behaviour stays identical in both places.
"""

from __future__ import annotations

import logging
from typing import Tuple

from django.db import connection

from .mail_manage.db_alert_email import send_db_inactive_alert

logger = logging.getLogger(__name__)


def run_db_health_check() -> Tuple[bool, str, bool]:
    """Run a `SELECT 1` against the database.

    Returns a tuple `(ok, reason, alert_sent)`:
      - ok: True if the DB responded, False otherwise.
      - reason: empty when ok=True, otherwise the exception text.
      - alert_sent: True if an alert email was successfully sent (only when
        ok=False).
    """
    print("[CRON] pinging DB with SELECT 1...", flush=True)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
    except Exception as exc:
        print(f"[CRON] DB is DOWN - error: {exc}", flush=True)
        logger.warning("DB health check failed: %s", exc)
        sent = send_db_inactive_alert(reason=str(exc))
        print(f"[CRON] alert email send result: {sent}", flush=True)
        return False, str(exc), sent

    print(f"[CRON] DB is UP - SELECT 1 returned {row}", flush=True)
    return True, "", False
