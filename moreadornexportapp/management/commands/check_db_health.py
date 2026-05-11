"""Local DB health-check runner.

Usage:
    python manage.py check_db_health              # one shot
    python manage.py check_db_health --loop 60    # forever, every 60 sec

Hits the same `run_db_health_check()` helper the Vercel cron uses, so the
output you see here is exactly what would print in Vercel function logs.
"""

from __future__ import annotations

import time
from datetime import datetime

from django.core.management.base import BaseCommand

from moreadornexportapp.db_health import run_db_health_check


class Command(BaseCommand):
    help = "Run the DB health check (same logic as the Vercel cron)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            type=int,
            default=0,
            metavar="SECONDS",
            help=(
                "Run continuously, sleeping SECONDS between checks. "
                "Default 0 = single run."
            ),
        )

    def handle(self, *args, **opts):
        interval = opts["loop"]

        if interval <= 0:
            print(f"[CRON] {datetime.now().isoformat()} - single run", flush=True)
            run_db_health_check()
            return

        print(
            f"[CRON] loop mode - checking every {interval}s. Ctrl+C to stop.",
            flush=True,
        )
        try:
            while True:
                print(f"[CRON] tick @ {datetime.now().isoformat()}", flush=True)
                run_db_health_check()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("[CRON] stopped by user", flush=True)
