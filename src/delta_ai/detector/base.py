from __future__ import annotations

from abc import ABC, abstractmethod

from delta_ai.types import Detection, Frame


class DetectorBackend(ABC):
    @abstractmethod
    def detect(self, frame: Frame) -> list[Detection]:
        """Return detections for the provided frame."""

