from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter, sleep

from delta_ai.capture.base import CaptureBackend
from delta_ai.config import InputConfig, RuntimeConfig
from delta_ai.controller.selector import target_to_cursor_command
from delta_ai.detector.base import DetectorBackend
from delta_ai.input.base import CursorBackend
from delta_ai.tracker.base import TrackerBackend


@dataclass(slots=True)
class PipelineTimings:
    """单次主循环各阶段耗时。"""

    capture_ms: float
    detect_ms: float
    track_ms: float
    control_ms: float
    total_ms: float


@dataclass(slots=True)
class PipelineStats:
    """主循环统计结果。"""

    tick_count: int
    avg_capture_ms: float
    avg_detect_ms: float
    avg_track_ms: float
    avg_control_ms: float
    avg_total_ms: float


class Pipeline:
    def __init__(
        self,
        capture: CaptureBackend,
        detector: DetectorBackend,
        tracker: TrackerBackend,
        cursor: CursorBackend,
        runtime_config: RuntimeConfig,
        input_config: InputConfig,
    ) -> None:
        self.capture = capture
        self.detector = detector
        self.tracker = tracker
        self.cursor = cursor
        self.runtime_config = runtime_config
        self.input_config = input_config

    def tick(self) -> PipelineTimings:
        """执行一次采集、检测、追踪与控制。"""
        start = perf_counter()

        capture_start = perf_counter()
        frame = self.capture.grab()
        capture_ms = (perf_counter() - capture_start) * 1000

        detect_start = perf_counter()
        detections = self.detector.detect(frame)
        detect_ms = (perf_counter() - detect_start) * 1000

        track_start = perf_counter()
        target = self.tracker.update(detections)
        track_ms = (perf_counter() - track_start) * 1000

        control_start = perf_counter()
        command = target_to_cursor_command(target=target, frame=frame, input_config=self.input_config)
        if command is not None:
            self.cursor.move(command)
        control_ms = (perf_counter() - control_start) * 1000

        total_ms = (perf_counter() - start) * 1000
        return PipelineTimings(
            capture_ms=capture_ms,
            detect_ms=detect_ms,
            track_ms=track_ms,
            control_ms=control_ms,
            total_ms=total_ms,
        )

    def run(self) -> list[PipelineTimings]:
        """按运行时配置执行持续监测循环。"""
        if not self.runtime_config.continuous_mode:
            return [self.tick()]

        timings_history: list[PipelineTimings] = []
        tick_index = 0
        tick_interval_s = 1.0 / self.runtime_config.target_fps

        while True:
            loop_start = perf_counter()
            timings_history.append(self.tick())
            tick_index += 1

            if 0 < self.runtime_config.max_ticks <= tick_index:
                break

            elapsed_s = perf_counter() - loop_start
            remaining_s = tick_interval_s - elapsed_s
            if remaining_s > 0:
                sleep(remaining_s)

        return timings_history


def summarize_timings(timings_history: list[PipelineTimings]) -> PipelineStats:
    """汇总多次主循环的平均耗时。"""
    tick_count = len(timings_history)
    if tick_count == 0:
        return PipelineStats(
            tick_count=0,
            avg_capture_ms=0.0,
            avg_detect_ms=0.0,
            avg_track_ms=0.0,
            avg_control_ms=0.0,
            avg_total_ms=0.0,
        )

    capture_total = sum(item.capture_ms for item in timings_history)
    detect_total = sum(item.detect_ms for item in timings_history)
    track_total = sum(item.track_ms for item in timings_history)
    control_total = sum(item.control_ms for item in timings_history)
    total_total = sum(item.total_ms for item in timings_history)

    return PipelineStats(
        tick_count=tick_count,
        avg_capture_ms=capture_total / tick_count,
        avg_detect_ms=detect_total / tick_count,
        avg_track_ms=track_total / tick_count,
        avg_control_ms=control_total / tick_count,
        avg_total_ms=total_total / tick_count,
    )
