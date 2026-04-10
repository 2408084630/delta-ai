from __future__ import annotations

from delta_ai.config import InputConfig
from delta_ai.types import CursorCommand, Frame, TargetState


def target_to_cursor_command(
    target: TargetState | None,
    frame: Frame,
    input_config: InputConfig,
) -> CursorCommand | None:
    """把当前目标转换成鼠标命令。

    检测器输出的是 ROI 内部坐标，这里负责把它映射回屏幕绝对坐标。
    """
    if target is None:
        return None

    detection = target.detection
    scale_x = _safe_scale(frame.source_width, frame.width)
    scale_y = _safe_scale(frame.source_height, frame.height)

    screen_x = frame.screen_left + (detection.x * scale_x) + input_config.offset_x
    screen_y = frame.screen_top + (detection.y * scale_y) + input_config.offset_y

    return CursorCommand(x=screen_x, y=screen_y, relative_to_screen=True)


def _safe_scale(source_size: int, frame_size: int) -> float:
    """计算从处理后图像到原始 ROI 的缩放比例。"""
    if source_size <= 0 or frame_size <= 0:
        return 1.0
    return source_size / frame_size
