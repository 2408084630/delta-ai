# delta-ai

Low-latency screen perception prototype for continuous ROI capture, target detection, tracking, and cursor control.

## Phase 1

The first milestone is a runnable project skeleton with clear boundaries between:

- screen capture
- detection
- tracking
- control loop
- cursor output
- configuration and profiling

This keeps the latency-critical path easy to measure and optimize.

## Proposed MVP

1. Capture the center ROI from a single display.
2. Run lightweight target detection on the latest frame only.
3. Smooth or maintain target state with a tracker.
4. Emit a target point to a cursor adapter.
5. Log per-stage timings for end-to-end latency analysis.

## Project Layout

```text
src/delta_ai/
  capture/
  controller/
  detector/
  input/
  tracker/
  config.py
  pipeline.py
  main.py
```

## Next Steps

1. Add a real ROI capture backend.
2. Add an ONNX/TensorRT detector adapter.
3. Add a simple tracker and timing profiler.
4. Benchmark whether the target hardware can sustain the latency budget.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

delta-ai
```

如果要启用 `ultralytics` 版 YOLO 检测器，可以安装可选依赖：

```bash
pip install -e ".[yolo]"
```

如果要启用真实鼠标输出 backend，可以安装输入控制依赖：

```bash
pip install -e ".[input]"
```

如果当前环境还没有安装依赖，也可以先用下面的方式验证项目入口：

```bash
PYTHONPATH=src python3 -m delta_ai
```

## Current Status

当前已经具备以下能力：

- 单屏中心 ROI 参数化配置
- `mss` 屏幕采集 backend
- 持续监测主循环骨架
- 可切换的检测器工厂
- `ultralytics` YOLO 检测器适配层
- 可切换的鼠标输出工厂
- ROI 坐标到屏幕绝对坐标的映射
- ROI 坐标计算与边界保护
- 每次采集返回屏幕绝对坐标信息，方便后续做鼠标映射

如果没有安装 YOLO 依赖或没有提供模型文件，程序会自动退回 stub 检测器。
