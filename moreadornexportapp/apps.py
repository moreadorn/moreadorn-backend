import os
import sys
import threading

from django.apps import AppConfig


class MoreadornexportappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moreadornexportapp"

    def ready(self):
        if not _should_start_local_cron():
            return

        from decouple import config

        interval = config("LOCAL_CRON_INTERVAL", default=7200, cast=int)

        thread = threading.Thread(
            target=_local_cron_loop,
            args=(interval,),
            daemon=True,
            name="db-health-cron",
        )
        thread.start()
        print(
            f"[CRON] local scheduler started - every {interval}s "
            f"(set LOCAL_CRON_INTERVAL in .env to change)",
            flush=True,
        )


def _should_start_local_cron() -> bool:
    """Only spin up the in-process scheduler under `runserver`.

    On Vercel the Vercel Cron entry in `vercel.json` triggers the same
    logic over HTTP, so we skip the in-process thread in production.
    """
    if "runserver" not in sys.argv:
        return False
    # `runserver` auto-reload spawns parent + child. Only run in the child
    # to avoid double-firing. With `--noreload` there is just one process
    # and RUN_MAIN is unset, so allow it through.
    if "--noreload" not in sys.argv and os.environ.get("RUN_MAIN") != "true":
        return False
    return True


def _local_cron_loop(interval: int):
    import time
    from datetime import datetime

    from .db_health import run_db_health_check

    while True:
        try:
            print(f"[CRON] tick @ {datetime.now().isoformat()}", flush=True)
            run_db_health_check()
        except Exception as exc:
            print(f"[CRON] tick error: {exc}", flush=True)
        time.sleep(interval)
