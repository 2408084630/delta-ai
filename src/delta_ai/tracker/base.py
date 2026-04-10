from __future__ import annotations

from abc import ABC, abstractmethod

from delta_ai.types import Detection, TargetState


class TrackerBackend(ABC):
    @abstractmethod
    def update(self, detections: list[Detection]) -> TargetState | None:
        """Return the active target for the current frame."""

