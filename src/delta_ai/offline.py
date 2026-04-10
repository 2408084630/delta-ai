from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from delta_ai.config import AppConfig
from delta_ai.detector.factory import create_detector_backend
from delta_ai.types import Frame
from delta_ai.visualization import save_annotated_image


def main() -> None:
    """离线图片检测入口。"""
    args = _parse_args()
    config = _build_config_from_args(args)
    image_array = _load_image_array(args.image)

    frame = Frame(
        width=int(image_array.shape[1]),
        height=int(image_array.shape[0]),
        pixels=image_array,
        screen_left=0,
        screen_top=0,
        source_width=int(image_array.shape[1]),
        source_height=int(image_array.shape[0]),
    )

    detector = create_detector_backend(config)
    detections = detector.detect(frame)

    print(f"detector={config.detection.detector_type}")
    print(f"detections={len(detections)}")
    for index, detection in enumerate(detections, start=1):
        print(
            f"[{index}]",
            f"label={detection.label}",
            f"confidence={detection.confidence:.3f}",
            f"center=({detection.x:.1f},{detection.y:.1f})",
            f"size=({detection.width:.1f},{detection.height:.1f})",
        )

    if args.output:
        save_annotated_image(image_array=image_array, detections=detections, output_path=args.output)
        print(f"annotated_output={args.output}")


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="离线图片检测与标注工具。")
    parser.add_argument("--image", required=True, help="待检测图片路径。")
    parser.add_argument("--output", default="", help="可选，保存标注图的输出路径。")
    parser.add_argument(
        "--detector",
        default="debug",
        choices=["debug", "stub", "ultralytics"],
        help="检测器类型，默认使用 debug 便于先做链路联调。",
    )
    parser.add_argument("--model-path", default="", help="YOLO 模型文件路径。")
    parser.add_argument("--imgsz", type=int, default=320, help="YOLO 输入尺寸。")
    parser.add_argument("--conf", type=float, default=0.35, help="YOLO 置信度阈值。")
    parser.add_argument("--iou", type=float, default=0.45, help="YOLO 的 IoU 阈值。")
    return parser.parse_args()


def _build_config_from_args(args: argparse.Namespace) -> AppConfig:
    """根据命令行参数构造配置。"""
    config = AppConfig()
    config.detection.detector_type = args.detector
    config.detection.model_path = args.model_path
    config.detection.image_size = args.imgsz
    config.detection.confidence_threshold = args.conf
    config.detection.iou_threshold = args.iou
    return config


def _load_image_array(image_path: str) -> np.ndarray:
    """读取图片并转换为 numpy 数组。"""
    path = Path(image_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"图片不存在：{path}")

    image = Image.open(path).convert("RGB")
    return np.asarray(image)
