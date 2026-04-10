from __future__ import annotations

try:
    from pynput.mouse import Controller
except ImportError:  # pragma: no cover - 可选依赖缺失时允许项目继续导入
    Controller = None

from delta_ai.config import AppConfig
from delta_ai.input.base import CursorBackend
from delta_ai.types import CursorCommand


class PynputCursorBackend(CursorBackend):
    """基于 pynput 的鼠标输出 backend。"""

    def __init__(self, config: AppConfig) -> None:
        if Controller is None:
            raise RuntimeError("未安装 pynput，无法启用真实鼠标输出。")

        self.config = config
        try:
            self.controller = Controller()
        except Exception as exc:  # pragma: no cover - 依赖系统环境
            raise RuntimeError(f"创建 pynput Controller 失败：{exc}") from exc

    def move(self, command: CursorCommand) -> None:
        """把鼠标移动到屏幕绝对坐标。"""
        target_x = int(round(command.x))
        target_y = int(round(command.y))

        if self.config.input.clamp_to_screen:
            target_x, target_y = self._clamp_to_monitor(target_x, target_y)

        try:
            self.controller.position = (target_x, target_y)
        except Exception as exc:  # pragma: no cover - 依赖系统环境
            raise RuntimeError(f"设置鼠标位置失败：{exc}") from exc

    def _clamp_to_monitor(self, x: int, y: int) -> tuple[int, int]:
        """把鼠标坐标限制到当前目标屏幕边界内。"""
        # 这里复用单屏前提，直接根据 monitor_index 绑定的物理屏幕做限制。
        # 后续如果要支持多屏自动切换，可以把屏幕信息抽到共享上下文中。
        try:
            import mss
        except ImportError:
            return x, y

        with mss.mss() as sct:
            monitor = sct.monitors[self.config.capture.monitor_index]

        min_x = int(monitor["left"])
        min_y = int(monitor["top"])
        max_x = min_x + int(monitor["width"]) - 1
        max_y = min_y + int(monitor["height"]) - 1

        clamped_x = min(max(x, min_x), max_x)
        clamped_y = min(max(y, min_y), max_y)
        return clamped_x, clamped_y
