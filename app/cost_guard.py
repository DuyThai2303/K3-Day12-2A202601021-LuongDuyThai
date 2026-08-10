"""Module Cost Guard quản lý ngân sách người dùng theo tháng (CP3)."""

from datetime import datetime, timezone
from fastapi import HTTPException, status
import redis


class CostGuard:

    def __init__(self, redis_client: redis.Redis, monthly_budget_usd: float = 10.0):
        self.client = redis_client
        self.budget_usd = monthly_budget_usd

    @staticmethod
    def _key(user_id: str, now: datetime | None = None) -> str:
        now = now if now is not None else datetime.now(timezone.utc)
        month_str = now.strftime("%Y-%m")
        return f"cost:{user_id}:{month_str}"

    def spent(self, user_id: str, now: datetime | None = None) -> float:
        """Trả về số tiền đã tiêu tốn của user trong tháng hiện tại."""
        key = self._key(user_id, now)
        val = self.client.get(key)
        return float(val) if val else 0.0

    def check(self, user_id: str, estimated_cost: float = 0.0, now: datetime | None = None) -> None:
        """Kiểm tra nếu chi phí hiện tại + ước tính lớn hơn budget -> raise 402."""
        current_spent = self.spent(user_id, now)
        if current_spent + estimated_cost > self.budget_usd:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="monthly budget exceeded",
            )

    def record(self, user_id: str, cost_usd: float, now: datetime | None = None) -> float:
        """Cộng dồn chi phí thực tế sau khi gọi LLM thành công."""
        key = self._key(user_id, now)
        new_total = self.client.incrbyfloat(key, cost_usd)
        return float(new_total)