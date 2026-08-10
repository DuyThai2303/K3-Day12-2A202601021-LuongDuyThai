"""Module Rate Limiter dạng Sliding Window sử dụng Redis (CP3)."""

import time
import uuid
from fastapi import HTTPException, status
import redis

WINDOW_SECONDS = 60


class RateLimiter:

    def __init__(self, redis_client: redis.Redis, limit_per_minute: int = 10):
        self.client = redis_client
        self.limit = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        return f"rate_limit:{user_id}"

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        """Đếm số request hợp lệ trong cửa sổ 60s hiện tại."""
        now = now if now is not None else time.time()
        key = self._key(user_id)
        # Prune các entry cũ hơn 60s
        self.client.zremrangebyscore(key, 0, now - WINDOW_SECONDS)
        return int(self.client.zcard(key))

    def check(self, user_id: str, now: float | None = None) -> None:
        """Cho qua nếu còn quota, ngược lại raise HTTP 429."""
        now = now if now is not None else time.time()
        key = self._key(user_id)

        count = self.hit_count(user_id, now)

        if count >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        # Ghi nhận request bằng member chứa UUID chống trùng timestamp
        self.client.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        self.client.expire(key, WINDOW_SECONDS)