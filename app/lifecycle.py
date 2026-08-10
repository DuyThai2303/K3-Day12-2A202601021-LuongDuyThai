"""Module quản lý vòng đời ứng dụng và Graceful Shutdown (CP4)."""

import signal


class Lifecycle:

    def __init__(self):
        self.shutting_down = False
        self._old_handlers = {}

    def request_shutdown(self, signum=None, frame=None):
        """Đánh dấu cờ shutting_down và nhường quyền gọi lại handler cũ (nếu có)."""
        self.shutting_down = True

        # Nếu có signal handler cũ (ví dụ uvicorn/system), gọi lại handler đó
        if signum is not None and signum in self._old_handlers:
            old_handler = self._old_handlers[signum]
            if callable(old_handler):
                old_handler(signum, frame)

    def install(self):
        """Đăng ký handler cho tín hiệu SIGTERM và SIGINT."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            old_h = signal.signal(sig, self.request_shutdown)
            if old_h is not None:
                self._old_handlers[sig] = old_h


lifecycle = Lifecycle()