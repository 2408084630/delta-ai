from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass(slots=True)
class Frame:
    """采集帧对象。"""

    # 当前帧像素数据的宽度。
    width: int
    # 当前帧像素数据的高度。
    height: int
    # 当前帧产生的时间戳，使用高精度计时器。
    timestamp: float = field(default_factory=perf_counter)
    # 像素数据本体。
    pixels: object | None = None
    # ROI 在屏幕绝对坐标中的左上角 x。
    screen_left: int = 0
    # ROI 在屏幕绝对坐标中的左上角 y。
    screen_top: int = 0
    # ROI 对应的原始屏幕区域宽度。
    source_width: int = 0
    # ROI 对应的原始屏幕区域高度。
    source_height: int = 0


@dataclass(slots=True)
class Detection:
    """检测结果。"""

    label: str
    confidence: float
    x: float
    y: float
    width: float
    height: float


@dataclass(slots=True)
class TargetState:
    """追踪后的目标状态。"""

    detection: Detection
    stable: bool = False


@dataclass(slots=True)
class CursorCommand:
    """鼠标移动命令。"""

    # 鼠标的屏幕绝对 x 坐标。
    x: float
    # 鼠标的屏幕绝对 y 坐标。
    y: float
    # 是否已经是屏幕绝对坐标。
    # 当前控制层默认输出绝对坐标，保留这个字段是为了后续兼容相对移动模式。
    relative_to_screen: bool = True
