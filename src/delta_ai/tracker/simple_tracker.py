from __future__ import annotations

from delta_ai.tracker.base import TrackerBackend
from delta_ai.types import Detection, TargetState


class SimpleTracker(TrackerBackend):
    """简单目标追踪器。

    当前版本仅选择最高置信度目标，目的是先打通持续监测链路。
    后续可以替换成带轨迹关联和目标保持能力的真正 tracker。
    """

    def update(self, detections: list[Detection]) -> TargetState | None:
        if not detections:
            return None

        best_detection = max(detections, key=lambda item: item.confidence)
        return TargetState(detection=best_detection, stable=True)
