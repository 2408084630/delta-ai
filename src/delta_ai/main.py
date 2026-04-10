from __future__ import annotations

from delta_ai.capture.factory import create_capture_backend
from delta_ai.config import AppConfig
from delta_ai.detector.factory import create_detector_backend
from delta_ai.input.factory import create_cursor_backend
from delta_ai.pipeline import Pipeline, summarize_timings
from delta_ai.tracker.simple_tracker import SimpleTracker


def main() -> None:
    # 当前阶段先把关键参数集中到配置对象中，后续接检测器与持续循环时继续扩展。
    config = AppConfig()
    pipeline = Pipeline(
        capture=create_capture_backend(config),
        detector=create_detector_backend(config),
        tracker=SimpleTracker(),
        cursor=create_cursor_backend(config),
        runtime_config=config.runtime,
        input_config=config.input,
    )
    timings_history = pipeline.run()
    stats = summarize_timings(timings_history)
    print(
        "pipeline summary",
        f"roi={config.roi.width_ratio:.2f}x{config.roi.height_ratio:.2f}",
        f"downscale={config.roi.downscale_factor:.2f}",
        f"detector={config.detection.detector_type}",
        f"input={config.input.backend_type}",
        f"input_enabled={config.input.enabled}",
        f"ticks={stats.tick_count}",
        f"avg_capture={stats.avg_capture_ms:.3f}ms",
        f"avg_detect={stats.avg_detect_ms:.3f}ms",
        f"avg_track={stats.avg_track_ms:.3f}ms",
        f"avg_control={stats.avg_control_ms:.3f}ms",
        f"avg_total={stats.avg_total_ms:.3f}ms",
    )


if __name__ == "__main__":
    main()
