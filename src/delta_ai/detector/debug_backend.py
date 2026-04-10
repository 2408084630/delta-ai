from __future__ import annotations

from delta_ai.config import AppConfig
from delta_ai.detector.base import DetectorBackend
from delta_ai.types import Detection, Frame


class DebugDetectorBackend(DetectorBackend):
    """固定框调试检测器。

    用于在没有模型权重时快速验证：
    - ROI 到屏幕坐标的映射
    - 鼠标输出链路
    - 标注可视化是否正确
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def detect(self, frame: Frame) -> list[Detection]:
        """在当前帧内生成一个固定比例的测试框。"""
        width = max(1.0, frame.width * self.config.detection.debug_box_width_ratio)
        height = max(1.0, frame.height * self.config.detection.debug_box_height_ratio)
        center_x = frame.width * self.config.detection.debug_center_x_ratio
        center_y = frame.height * self.config.detection.debug_center_y_ratio

        return [
            Detection(
                label=self.config.detection.debug_label,
                confidence=self.config.detection.debug_confidence,
                x=float(center_x),
                y=float(center_y),
                width=float(width),
                height=float(height),
            )
        ]
