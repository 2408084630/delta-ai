from __future__ import annotations

from dataclasses import dataclass

try:
    import mss
except ImportError:  # pragma: no cover - 依赖未安装时允许项目继续导入
    mss = None

try:
    import numpy as np
except ImportError:  # pragma: no cover - 依赖未安装时允许项目继续导入
    np = None

from delta_ai.capture.base import CaptureBackend
from delta_ai.capture.roi import RoiBounds, compute_center_roi
from delta_ai.config import AppConfig
from delta_ai.types import Frame


@dataclass(slots=True)
class MonitorInfo:
    """屏幕信息。"""

    # 屏幕左上角 x 坐标。
    left: int
    # 屏幕左上角 y 坐标。
    top: int
    # 屏幕宽度。
    width: int
    # 屏幕高度。
    height: int


class MssCaptureBackend(CaptureBackend):
    """基于 mss 的单屏 ROI 采集 backend。"""

    def __init__(self, config: AppConfig) -> None:
        if mss is None or np is None:
            raise RuntimeError("缺少 mss 或 numpy 依赖，无法启用真实屏幕采集 backend。")

        self.config = config
        self._sct = mss.mss()
        self._monitor = self._load_monitor()
        self._roi = self._build_roi()
        self._warmup()

    def grab(self) -> Frame:
        """抓取一帧当前 ROI。

        返回的 `pixels` 是一个 `numpy.ndarray`，格式为 BGRA。
        这样后续接 OpenCV 或 ONNX 前处理时可以减少一次额外转换。
        """
        screenshot = self._sct.grab(
            {
                "left": self._roi.left,
                "top": self._roi.top,
                "width": self._roi.width,
                "height": self._roi.height,
            }
        )
        pixels = np.asarray(screenshot)
        pixels = self._maybe_downscale(pixels)

        return Frame(
            width=int(pixels.shape[1]),
            height=int(pixels.shape[0]),
            pixels=pixels,
            screen_left=self._roi.left,
            screen_top=self._roi.top,
            source_width=self._roi.width,
            source_height=self._roi.height,
        )

    def _load_monitor(self) -> MonitorInfo:
        """读取目标物理屏幕信息。"""
        monitor_index = self.config.capture.monitor_index
        monitors = self._sct.monitors

        if monitor_index >= len(monitors):
            raise ValueError(
                f"monitor_index={monitor_index} 超出可用屏幕范围，当前仅检测到 {len(monitors) - 1} 块物理屏幕。"
            )

        monitor = monitors[monitor_index]
        return MonitorInfo(
            left=int(monitor["left"]),
            top=int(monitor["top"]),
            width=int(monitor["width"]),
            height=int(monitor["height"]),
        )

    def _build_roi(self) -> RoiBounds:
        """构造当前采集 ROI。"""
        if not self.config.capture.center_locked:
            raise NotImplementedError("当前版本只支持中心 ROI 采集。")

        return compute_center_roi(
            screen_left=self._monitor.left,
            screen_top=self._monitor.top,
            screen_width=self._monitor.width,
            screen_height=self._monitor.height,
            roi_config=self.config.roi,
        )

    def _warmup(self) -> None:
        """预热采集 backend，减少首帧抖动。"""
        warmup_frames = self.config.capture.warmup_frames
        for _ in range(warmup_frames):
            self._sct.grab(
                {
                    "left": self._roi.left,
                    "top": self._roi.top,
                    "width": self._roi.width,
                    "height": self._roi.height,
                }
            )

    def _maybe_downscale(self, pixels: "np.ndarray") -> "np.ndarray":
        """按配置做最简单的步长降采样。

        这里先不用 OpenCV，目的是保持第二步依赖最小。
        如果后续接入 OpenCV，可以替换成更高质量的 resize。
        """
        downscale_factor = self.config.roi.downscale_factor
        if downscale_factor >= 1.0:
            return pixels

        step = max(1, int(round(1.0 / downscale_factor)))
        return pixels[::step, ::step]
