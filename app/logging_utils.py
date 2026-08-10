"""Hỗ trợ Structured Logging dạng JSON cho ứng dụng (CP1)."""

import json
import sys
from datetime import datetime, timezone


def log_event(event_name: str, level: str = "info", **kwargs) -> str:
    """Ghi log sự kiện theo định dạng JSON cấu trúc.

    Yêu cầu:
    1. Tự động bổ sung timestamp theo định dạng ISO 8601 (UTC).
    2. Chuẩn hóa `level` thành chữ viết thường ("info", "error",...).
    3. In chuỗi JSON ra `sys.stdout` trên một dòng duy nhất.
    4. Trả về chuỗi JSON (str) để phục vụ việc kiểm thử unit test.
    """
    level_str = str(level).lower()

    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level_str,
        "event": event_name,
    }

    # Nối thêm các tham số tùy ý (ví dụ: user_id, cost_usd, latency_ms,...)
    log_data.update(kwargs)

    # Chuyển đổi dict thành chuỗi JSON
    json_str = json.dumps(log_data, ensure_ascii=False)

    # In ra stdout (bắt buộc flush=True để pytest và Docker collector bắt được log ngay)
    print(json_str, file=sys.stdout, flush=True)

    # Trả về chuỗi JSON
    return json_str