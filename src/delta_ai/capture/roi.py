from __future__ import annotations

from dataclasses import dataclass

from delta_ai.config import RoiConfig


@dataclass(slots=True)
class RoiBounds:
    """屏幕 ROI 边界信息。"""

    # ROI 左上角 x 坐标。
    left: int
    # ROI 左上角 y 坐标。
    top: int
    # ROI 宽度。
    width: int
    # ROI 高度。
    height: int


def compute_center_roi(
    screen_left: int,
    screen_top: int,
    screen_width: int,
    screen_height: int,
    roi_config: RoiConfig,
) -> RoiBounds:
    """根据屏幕尺寸计算中心 ROI。

    这里统一在整数像素空间内做截断，避免后续采集和坐标换算出现半像素误差。
    """
    roi_width = max(1, int(screen_width * roi_config.width_ratio))
    roi_height = max(1, int(screen_height * roi_config.height_ratio))

    left = screen_left + max(0, (screen_width - roi_width) // 2)
    top = screen_top + max(0, (screen_height - roi_height) // 2)

    return RoiBounds(
        left=left,
        top=top,
        width=min(roi_width, screen_width),
        height=min(roi_height, screen_height),
    )
