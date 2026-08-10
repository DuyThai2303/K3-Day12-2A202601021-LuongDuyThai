"""Module ConversationStore quản lý lịch sử trò chuyện bằng Redis (CP4)."""

from __future__ import annotations

import json
import redis

# Hằng số cấu hình được test_cp4.py yêu cầu import
HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 86400 * 7  # 7 ngày TTL


class ConversationStore:

    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    @staticmethod
    def _key(user_id: str) -> str:
        return f"history:{user_id}"

    def get_history(self, user_id: str) -> list[dict[str, str]]:
        """Lấy danh sách lịch sử hội thoại của user từ Redis."""
        key = self._key(user_id)
        raw = self.client.get(key)
        if not raw:
            return []
        try:
            return json.loads(raw)
        except Exception:
            return []

    def append(self, user_id: str, role: str, content: str) -> list[dict[str, str]]:
        """Thêm tin nhắn mới, cắt bớt nếu quá dài và cập nhật TTL cho key."""
        history = self.get_history(user_id)
        history.append({"role": role, "content": content})

        # Cắt bớt lịch sử chỉ giữ lại HISTORY_MAX_MESSAGES tin nhắn gần nhất
        if len(history) > HISTORY_MAX_MESSAGES:
            history = history[-HISTORY_MAX_MESSAGES:]

        key = self._key(user_id)
        # Lưu đè danh sách và thiết lập thời gian hết hạn TTL
        self.client.set(key, json.dumps(history, ensure_ascii=False), ex=HISTORY_TTL_SECONDS)
        return history

    def clear(self, user_id: str) -> None:
        """Xóa lịch sử trò chuyện."""
        key = self._key(user_id)
        self.client.delete(key)

    def ping(self) -> bool:
        """Kiểm tra kết nối Redis cho readiness probe."""
        try:
            return bool(self.client.ping())
        except Exception:
            return False


def get_redis_client(redis_url: str | None = None) -> redis.Redis:
    """Tạo kết nối Redis client an toàn, không làm sập Server khi URL lỗi."""
    if redis_url is None:
        try:
            from app.config import get_settings
            redis_url = get_settings().redis_url
        except Exception:
            redis_url = "fake://"

    # Nếu URL trống hoặc dùng fake:// -> Trả về Redis giả trong RAM
    if not redis_url or str(redis_url).startswith("fake://"):
        import fakeredis
        return fakeredis.FakeRedis(decode_responses=True)

    try:
        return redis.Redis.from_url(redis_url, decode_responses=True)
    except Exception:
        # Nếu chuỗi URL Redis bị lỗi cấu hình -> Fallback an toàn về fakeredis
        import fakeredis
        return fakeredis.FakeRedis(decode_responses=True)