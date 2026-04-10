from __future__ import annotations

import sys

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
        print("cursor backend: 已禁用真实鼠标输出，当前使用 StubCursor。", file=sys.stderr)
        return StubCursor()

    if backend_type == "pynput":
        try:
            return PynputCursorBackend(config=config)
        except RuntimeError as exc:
            print(f"cursor backend: pynput 初始化失败，已回退到 StubCursor。原因：{exc}", file=sys.stderr)
            return StubCursor()

    print(f"cursor backend: 不支持的 backend_type={backend_type}，已回退到 StubCursor。", file=sys.stderr)
    return StubCursor()
