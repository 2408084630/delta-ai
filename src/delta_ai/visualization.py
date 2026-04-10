from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from delta_ai.types import Detection


def save_annotated_image(
    image_array: np.ndarray,
    detections: list[Detection],
    output_path: str,
) -> None:
    """保存带检测框和中心点的标注图。"""
    image = _to_pil_image(image_array)
    draw = ImageDraw.Draw(image)

    for detection in detections:
        x1 = detection.x - detection.width / 2.0
        y1 = detection.y - detection.height / 2.0
        x2 = detection.x + detection.width / 2.0
        y2 = detection.y + detection.height / 2.0

        draw.rectangle((x1, y1, x2, y2), outline=(255, 0, 0), width=3)
        draw.ellipse(
            (detection.x - 4, detection.y - 4, detection.x + 4, detection.y + 4),
            fill=(0, 255, 0),
        )
        draw.text((x1, max(0, y1 - 18)), f"{detection.label} {detection.confidence:.2f}", fill=(255, 255, 0))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _to_pil_image(image_array: np.ndarray) -> Image.Image:
    """把 numpy 图像转换为 PIL Image。"""
    if image_array.ndim != 3:
        raise ValueError("仅支持三通道或四通道图像进行标注。")

    channels = image_array.shape[2]
    if channels == 4:
        # mss 默认输出 BGRA，这里转成 RGBA 便于标注保存。
        converted = image_array[:, :, [2, 1, 0, 3]]
        return Image.fromarray(converted, mode="RGBA")

    if channels == 3:
        return Image.fromarray(image_array, mode="RGB")

    raise ValueError(f"不支持的图像通道数：{channels}")
