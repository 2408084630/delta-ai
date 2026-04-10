from __future__ import annotations

from delta_ai.config import AppConfig
from delta_ai.input.base import CursorBackend
from delta_ai.input.pynput_backend import PynputCursorBackend
from delta_ai.stubs import StubCursor


def create_cursor_backend(config: AppConfig) -> CursorBackend:
    """创建鼠标输出 backend。

    当依赖未安装、权限未开启或配置明确要求不启用时，会自动退回 stub。
    """
    backend_type = config.input.backend_type.lower().strip()
    if not config.input.enabled:
        return StubCursor()

    if backend_type == "pynput":
        try:
            return PynputCursorBackend(config=config)
        except RuntimeError:
            return StubCursor()

    return StubCursor()
