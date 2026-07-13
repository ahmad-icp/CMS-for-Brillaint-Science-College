from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, status

WINDOW_SECONDS = 60
MAX_REQUESTS = 120
_BUCKETS: dict[str, Deque[float]] = defaultdict(deque)


def check_rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _BUCKETS[key]
    while bucket and bucket[0] <= now - WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_REQUESTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail={"code":"rate_limited","message":"Too many requests"})
    bucket.append(now)
