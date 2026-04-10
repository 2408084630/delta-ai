from __future__ import annotations

from delta_ai.capture.base import CaptureBackend
from delta_ai.capture.mss_backend import MssCaptureBackend
from delta_ai.config import AppConfig
from delta_ai.stubs import StubCapture


def create_capture_backend(config: AppConfig) -> CaptureBackend:
    """根据当前环境创建采集 backend。

    如果依赖尚未安装，则自动降级到 stub，确保项目骨架仍可运行。
    """
    try:
        return MssCaptureBackend(config=config)
    except RuntimeError:
        return StubCapture()
