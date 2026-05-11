"""Endpoints triggered by Vercel Cron Jobs.

These are not part of the public API - they are meant to be hit by the
scheduler defined in `vercel.json`. A shared bearer secret (CRON_SECRET)
gates access so random callers cannot trigger them.
"""

from __future__ import annotations

import logging

from decouple import config
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .db_health import run_db_health_check

logger = logging.getLogger(__name__)


class DBHealthCronView(APIView):
    """Ping the database; email the team if it is unreachable."""

    permission_classes = [permissions.AllowAny]
    authentication_classes: list = []

    def _authorized(self, request) -> bool:
        secret = config("CRON_SECRET", default="")
        if not secret:
            return True
        auth = request.headers.get("Authorization", "")
        return auth == f"Bearer {secret}"

    def _check(self, request):
        print("[CRON] db-health endpoint hit", flush=True)

        if not self._authorized(request):
            print("[CRON] UNAUTHORIZED - bad/missing CRON_SECRET header", flush=True)
            return Response(
                {"detail": "Unauthorized."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        ok, reason, alert_sent = run_db_health_check()

        if not ok:
            return Response(
                {"ok": False, "alert_sent": alert_sent, "reason": reason},
                status=status.HTTP_200_OK,
            )

        print("[CRON] done - returning ok=True", flush=True)
        return Response({"ok": True}, status=status.HTTP_200_OK)

    def get(self, request):
        return self._check(request)

    def post(self, request):
        return self._check(request)
