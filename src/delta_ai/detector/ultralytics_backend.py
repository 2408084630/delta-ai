from __future__ import annotations

from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - 可选依赖缺失时允许项目继续导入
    YOLO = None

from delta_ai.config import AppConfig
from delta_ai.detector.base import DetectorBackend
from delta_ai.types import Detection, Frame


class UltralyticsDetectorBackend(DetectorBackend):
    """基于 ultralytics 的 YOLO 检测 backend。"""

    def __init__(self, config: AppConfig) -> None:
        if YOLO is None:
            raise RuntimeError("未安装 ultralytics，无法启用 YOLO 检测器。")

        model_path = Path(config.detection.model_path).expanduser()
        if not model_path.is_file():
            raise RuntimeError(f"YOLO 模型文件不存在：{model_path}")

        self.config = config
        self.model = YOLO(str(model_path))
        self.device = "cuda:0" if config.detection.prefer_gpu else "cpu"

    def detect(self, frame: Frame) -> list[Detection]:
        """执行一次 YOLO 检测并把结果转换为统一结构。"""
        if frame.pixels is None:
            return []

        class_ids = list(self.config.detection.class_ids) or None
        results = self.model.predict(
            source=frame.pixels,
            imgsz=self.config.detection.image_size,
            conf=self.config.detection.confidence_threshold,
            iou=self.config.detection.iou_threshold,
            max_det=self.config.detection.max_detections,
            classes=class_ids,
            device=self.device,
            verbose=False,
        )
        return self._convert_results(results)

    def _convert_results(self, results: object) -> list[Detection]:
        """把 ultralytics 返回结果转换为内部 Detection 列表。"""
        converted: list[Detection] = []

        for result in results:
            names = getattr(result, "names", {})
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            xyxy_values = boxes.xyxy.tolist()
            confidence_values = boxes.conf.tolist()
            class_values = boxes.cls.tolist()

            for xyxy, confidence, class_id in zip(xyxy_values, confidence_values, class_values):
                x1, y1, x2, y2 = xyxy
                width = float(x2 - x1)
                height = float(y2 - y1)
                center_x = float(x1 + width / 2.0)
                center_y = float(y1 + height / 2.0)
                label = str(names.get(int(class_id), f"class_{int(class_id)}"))

                converted.append(
                    Detection(
                        label=label,
                        confidence=float(confidence),
                        x=center_x,
                        y=center_y,
                        width=width,
                        height=height,
                    )
                )

        converted.sort(key=lambda item: item.confidence, reverse=True)
        return converted
