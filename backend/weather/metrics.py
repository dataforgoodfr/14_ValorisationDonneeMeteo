"""Minimal Prometheus metrics exposition for API observability."""

from __future__ import annotations

import threading
import time
from collections import defaultdict

from django.http import HttpRequest, HttpResponse

_LOCK = threading.Lock()
_REQUESTS_TOTAL = 0
_REQUESTS_BY_PATH: defaultdict[str, int] = defaultdict(int)
_REQUEST_ERRORS = 0
_REQUEST_DURATION_SECONDS = 0.0


class PrometheusMetricsMiddleware:
    """Collects simple HTTP metrics for Prometheus scraping."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        path = request.path
        if path.startswith("/api/") or path == "/metrics/":
            global _REQUESTS_TOTAL, _REQUEST_ERRORS, _REQUEST_DURATION_SECONDS
            with _LOCK:
                _REQUESTS_TOTAL += 1
                _REQUESTS_BY_PATH[path] += 1
                _REQUEST_DURATION_SECONDS += duration
                if response.status_code >= 500:
                    _REQUEST_ERRORS += 1

        return response


def metrics_view(_: HttpRequest) -> HttpResponse:
    """Exposes Prometheus metrics in text format."""

    with _LOCK:
        total = _REQUESTS_TOTAL
        errors = _REQUEST_ERRORS
        duration = _REQUEST_DURATION_SECONDS
        by_path = dict(_REQUESTS_BY_PATH)

    average_duration = duration / total if total > 0 else 0.0
    lines = [
        "# HELP app_up App health status.",
        "# TYPE app_up gauge",
        "app_up 1",
        "# HELP app_http_requests_total Total number of tracked HTTP requests.",
        "# TYPE app_http_requests_total counter",
        f"app_http_requests_total {total}",
        "# HELP app_http_request_errors_total Total number of tracked 5xx responses.",
        "# TYPE app_http_request_errors_total counter",
        f"app_http_request_errors_total {errors}",
        "# HELP app_http_request_duration_seconds_total Sum of tracked request durations.",
        "# TYPE app_http_request_duration_seconds_total counter",
        f"app_http_request_duration_seconds_total {duration:.6f}",
        "# HELP app_http_request_duration_seconds_avg Average tracked request duration.",
        "# TYPE app_http_request_duration_seconds_avg gauge",
        f"app_http_request_duration_seconds_avg {average_duration:.6f}",
        "# HELP app_http_requests_by_path_total Tracked request count by request path.",
        "# TYPE app_http_requests_by_path_total counter",
    ]

    for path, count in sorted(by_path.items()):
        escaped_path = path.replace('"', r"\"")
        lines.append(
            f'app_http_requests_by_path_total{{path="{escaped_path}"}} {count}'
        )

    return HttpResponse(
        "\n".join(lines) + "\n", content_type="text/plain; version=0.0.4"
    )
