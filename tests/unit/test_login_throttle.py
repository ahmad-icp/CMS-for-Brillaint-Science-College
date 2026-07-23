from collections import defaultdict

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.core.login_throttle import LoginThrottle


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = defaultdict(int)
        self.expiries: dict[str, int] = {}

    def get(self, key: str):
        return self.values.get(key)

    def ttl(self, key: str) -> int:
        return self.expiries.get(key, -1)

    def incr(self, key: str) -> int:
        self.values[key] += 1
        return self.values[key]

    def expire(self, key: str, seconds: int) -> bool:
        self.expiries[key] = seconds
        return True

    def delete(self, key: str) -> int:
        existed = int(key in self.values)
        self.values.pop(key, None)
        self.expiries.pop(key, None)
        return existed


def test_failed_logins_are_throttled_without_storing_identity() -> None:
    redis = FakeRedis()
    throttle = LoginThrottle(redis)  # type: ignore[arg-type]

    for _ in range(settings.LOGIN_MAX_FAILURES):
        throttle.register_failure("127.0.0.1", "college-001", "admin@example.test")

    with pytest.raises(HTTPException) as exc_info:
        throttle.ensure_allowed("127.0.0.1", "college-001", "admin@example.test")

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers is not None
    assert "Retry-After" in exc_info.value.headers
    assert all("admin@example.test" not in key for key in redis.values)


def test_successful_login_resets_failure_counter() -> None:
    redis = FakeRedis()
    throttle = LoginThrottle(redis)  # type: ignore[arg-type]
    throttle.register_failure("127.0.0.1", "college-001", "admin")

    throttle.reset("127.0.0.1", "college-001", "admin")
    throttle.ensure_allowed("127.0.0.1", "college-001", "admin")

    assert not redis.values
