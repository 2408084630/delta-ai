from __future__ import annotations

from delta_ai.capture.base import CaptureBackend
from delta_ai.detector.base import DetectorBackend
from delta_ai.input.base import CursorBackend
from delta_ai.tracker.base import TrackerBackend
from delta_ai.types import CursorCommand, Detection, Frame, TargetState


class StubCapture(CaptureBackend):
    """采集 stub。

    当本机还未安装真实截图依赖时，先返回一个固定尺寸的空帧，
    保证主流程和计时代码可以提前联调。
    """

    def grab(self) -> Frame:
        return Frame(
            width=640,
            height=640,
            pixels=None,
            screen_left=0,
            screen_top=0,
            source_width=640,
            source_height=640,
        )


class StubDetector(DetectorBackend):
    """检测 stub。"""

    def detect(self, frame: Frame) -> list[Detection]:
        return []


class StubTracker(TrackerBackend):
    """追踪 stub。"""

    def update(self, detections: list[Detection]) -> TargetState | None:
        return None


class StubCursor(CursorBackend):
    """鼠标控制 stub。"""

    def move(self, command: CursorCommand) -> None:
        return None
