"""Health check endpoints for production monitoring."""

from django.http import JsonResponse
from django.db import connections, connection
from django.db.utils import OperationalError
from django.conf import settings
from django.utils import timezone
import time


def health_check(request):
    """
    Basic health check endpoint for load balancers.
    Returns 200 if the application is running.
    """
    return JsonResponse({
        "status": "healthy",
        "version": "1.0.0",
        "environment": "production" if not settings.DEBUG else "development",
        "timestamp": timezone.now().isoformat(),
    })


def readiness_check(request):
    """
    Readiness check - verifies database connectivity and app readiness.
    Used by Kubernetes/Render to know when to route traffic.
    """
    checks = {
        "database": False,
        "migrations": False,
    }
    status = 200

    try:
        connections["default"].ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            checks["database"] = result is not None and result[0] == 1
    except OperationalError:
        checks["database"] = False
        status = 503

    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        pending = executor.migration_plan(targets)
        checks["migrations"] = len(pending) == 0
    except Exception:
        checks["migrations"] = True

    all_ready = all(checks.values())

    return JsonResponse({
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": timezone.now().isoformat(),
    }, status=status)


def liveness_check(request):
    """
    Liveness check - verifies app is still responsive.
    Returns basic responsiveness info without hitting database.
    """
    start = time.perf_counter()

    response_data = {
        "status": "alive",
        "timestamp": timezone.now().isoformat(),
        "uptime_seconds": int(time.time() - getattr(liveness_check, "_start_time", time.time())),
    }

    response_data["response_time_ms"] = round((time.perf_counter() - start) * 1000, 2)

    return JsonResponse(response_data)


liveness_check._start_time = time.time()
