"""Cấu hình ứng dụng theo nguyên tắc 12-Factor App."""

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    port: int = 8000
    agent_api_key: str  # Bắt buộc — không để mặc định
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("agent_api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        """Kích hoạt Fail-fast nếu API Key không hợp lệ hoặc dùng placeholder."""
        value = value.strip()
        invalid_placeholders = {"", "changeme", "your-api-key", "doi-thanh-khoa-cua-rieng-ban"}
        if not value or value.lower() in invalid_placeholders:
            raise ValueError(
                "AGENT_API_KEY không hợp lệ! Vui lòng cấu hình chìa khóa bảo mật trong file .env"
            )
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Trả về Singleton Settings instance (được cache để tối ưu hiệu năng)."""
    return Settings()