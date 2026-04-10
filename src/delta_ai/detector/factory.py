from __future__ import annotations

from delta_ai.config import AppConfig
from delta_ai.detector.base import DetectorBackend
from delta_ai.detector.debug_backend import DebugDetectorBackend
from delta_ai.detector.ultralytics_backend import UltralyticsDetectorBackend
from delta_ai.stubs import StubDetector


def create_detector_backend(config: AppConfig) -> DetectorBackend:
    """创建检测 backend。

    当前策略：
    - 未配置模型或依赖未安装时，自动降级到 stub。
    - 后续可以在这里继续增加 ONNX 或 TensorRT backend。
    """
    detector_type = config.detection.detector_type.lower().strip()

    if detector_type == "debug":
        return DebugDetectorBackend(config=config)

    if detector_type == "ultralytics":
        try:
            return UltralyticsDetectorBackend(config=config)
        except RuntimeError:
            return StubDetector()

    return StubDetector()
