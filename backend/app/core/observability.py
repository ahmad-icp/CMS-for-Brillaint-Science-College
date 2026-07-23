from __future__ import annotations

import json
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("college_erp.requests")
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


def safe_request_id(candidate: str | None) -> str:
    """Return a log-safe request ID or create a new one."""
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid.uuid4())


def _event(name: str, **fields: object) -> str:
    return json.dumps({"event": name, **fields}, separators=(",", ":"), default=str)


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Add correlation IDs, security headers, and structured request logs."""

    def __init__(self, app: Any, security_headers: dict[str, str] | None = None) -> None:
        super().__init__(app)
        self.security_headers = security_headers or {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = safe_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                _event(
                    "request_failed",
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    duration_ms=round((time.perf_counter() - started) * 1000, 2),
                )
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        for name, value in self.security_headers.items():
            response.headers[name] = value

        logger.info(
            _event(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=duration_ms,
            )
        )
        return response
