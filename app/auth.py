"""Module xác thực API Key và định danh người dùng (CP3)."""

import secrets
from fastapi import Header, HTTPException, status
from app.config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> str:
    """Xác thực API Key và trả về user_id.

    - Nếu thiếu X-API-Key hoặc sai Key -> Ném HTTPException(401).
    - So sánh API Key bằng secrets.compare_digest để chống timing attack.
    - Nếu có X-User-Id -> Trả về X-User-Id.
    - Nếu không có X-User-Id -> Trả về ANONYMOUS_USER ("anonymous").
    """
    settings = get_settings()

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    # Chống timing attack bằng secrets.compare_digest
    if not secrets.compare_digest(x_api_key, settings.agent_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    return x_user_id if x_user_id else ANONYMOUS_USER