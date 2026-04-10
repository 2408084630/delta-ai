from __future__ import annotations

from abc import ABC, abstractmethod

from delta_ai.types import Frame


class CaptureBackend(ABC):
    @abstractmethod
    def grab(self) -> Frame:
        """Return the latest ROI frame."""

