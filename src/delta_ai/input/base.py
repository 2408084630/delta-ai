from __future__ import annotations

from abc import ABC, abstractmethod

from delta_ai.types import CursorCommand


class CursorBackend(ABC):
    @abstractmethod
    def move(self, command: CursorCommand) -> None:
        """Move the cursor according to the provided command."""

