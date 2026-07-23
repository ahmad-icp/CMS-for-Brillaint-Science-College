from __future__ import annotations

import hashlib
import logging

from fastapi import HTTPException, status
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger("college_erp.security")


class LoginThrottle:
    """Redis-backed failed-login throttle shared across API workers."""

    def __init__(self, client: Redis | None = None) -> None:
        self.client = client or Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=settings.READINESS_TIMEOUT_SECONDS,
            socket_timeout=settings.READINESS_TIMEOUT_SECONDS,
        )

    @staticmethod
    def _key(client_host: str, college_id: str, username: str) -> str:
        identity = f"{client_host}|{college_id.casefold()}|{username.casefold()}"
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        return f"college-erp:login-failures:{digest}"

    def ensure_allowed(self, client_host: str, college_id: str, username: str) -> None:
        key = self._key(client_host, college_id, username)
        try:
            raw_count = self.client.get(key)
            count = int(raw_count or 0)
            if count >= settings.LOGIN_MAX_FAILURES:
                ttl = self.client.ttl(key)
                retry_after = max(1, int(ttl)) if ttl and ttl > 0 else settings.LOGIN_FAILURE_WINDOW_SECONDS
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed sign-in attempts. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
        except HTTPException:
            raise
        except RedisError:
            logger.warning("login_throttle_unavailable", exc_info=True)

    def register_failure(self, client_host: str, college_id: str, username: str) -> None:
        key = self._key(client_host, college_id, username)
        try:
            count = self.client.incr(key)
            if count == 1:
                self.client.expire(key, settings.LOGIN_FAILURE_WINDOW_SECONDS)
        except RedisError:
            logger.warning("login_throttle_unavailable", exc_info=True)

    def reset(self, client_host: str, college_id: str, username: str) -> None:
        try:
            self.client.delete(self._key(client_host, college_id, username))
        except RedisError:
            logger.warning("login_throttle_unavailable", exc_info=True)


login_throttle = LoginThrottle()
