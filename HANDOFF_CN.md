# 项目交接简要

## 目标

做一个持续监测型桌面视觉工具：

- 采集单屏中心 ROI
- 识别人形目标
- 计算目标坐标
- 控制鼠标移动到目标位置

用户的硬指标目标是：

- 持续监测
- 从识别到开始移动尽量压到 `50ms` 内

## 已讨论出的关键结论

- 如果目标是固定 UI 元素，模板匹配可能更快。
- 当前目标不是固定 UI，而是“游戏中的人物”，存在不同姿态、皮肤、背景和遮挡，因此更接近实时目标检测问题。
- 对这种动态人物场景，YOLO 比模板匹配更合理。
- 仅靠“每帧 YOLO 检测 + 鼠标移动”，要稳定压进 `50ms` 很难。
- 更现实的方向是：
  - 继续压缩 ROI 和输入尺寸
  - 优化采集链路
  - 使用更快推理后端
  - 最终采用“检测 + 跟踪”混合方案

## 当前项目代码状态

当前仓库已经有以下模块骨架和基础实现：

- 屏幕采集
  - `src/delta_ai/capture/mss_backend.py`
  - 支持单屏中心 ROI
  - 支持降采样
- 检测器
  - `src/delta_ai/detector/debug_backend.py`
  - `src/delta_ai/detector/ultralytics_backend.py`
  - `src/delta_ai/detector/factory.py`
- 控制与主循环
  - `src/delta_ai/pipeline.py`
  - `src/delta_ai/controller/selector.py`
- 鼠标输出
  - `src/delta_ai/input/pynput_backend.py`
  - `src/delta_ai/input/factory.py`
- 离线验证
  - `src/delta_ai/offline.py`
  - `src/delta_ai/visualization.py`
- 配置
  - `src/delta_ai/config.py`
  - 关键参数都已提取，并配有中文注释

## 已验证通过的功能

### 1. 鼠标基础链路已打通

用 `debug detector` 和 `pynput` 验证过：

- 检测框中心点可以正确映射回屏幕绝对坐标
- 鼠标可以真实移动
- 实测鼠标移动到了屏幕正中心

一次测试输出：

- `cursor_backend=PynputCursorBackend`
- `avg_capture=18.186ms`
- `avg_control=11.320ms`
- `avg_total=29.523ms`

说明：

- 当前仅“采集 + 控制”基础链路就接近 `30ms`

### 2. 公开 YOLO 模型能识别人

使用公开模型 `yolov8n.pt` 对图片：

- `/Users/mm/Downloads/1682316436552.jpeg`

做了离线检测，结果：

- 检出 `1` 个 `person`
- 置信度约 `0.91`

生成文件：

- 模型：`/Users/mm/Desktop/delta-ai/yolov8n.pt`
- 标注图：`/Users/mm/Downloads/1682316436552_yolov8n.jpg`

## 已测性能数据

对 `1682316436552.jpeg` 使用 `yolov8n.pt` 做离线推理测试：

- 模型加载：`29.465ms`
- 首次推理：`86.931ms`
- 热启动平均推理：`43.909ms`
- 热启动最快：`40.773ms`
- 热启动最慢：`50.282ms`

当前粗略估算总链路：

- 采集约 `18ms`
- 推理约 `44ms`
- 控制约 `11ms`

合计约：

- `73ms`

结论：

- 以当前实现和当前模型配置来看，稳定低于 `50ms` 不现实

## 当前最合理的下一步

建议优先做一组更有意义的对比测试，而不是直接接实时闭环：

1. 测 `imgsz=320`
2. 测 `imgsz=416`
3. 测中心 ROI 裁剪后的小图推理
4. 记录每组是否还能稳定检出人物
5. 比较耗时和精度

如果小尺寸下还能稳定识别，说明还有优化空间。  
如果小尺寸下识别率明显下降，则需要考虑：

- 更强模型
- 更好的数据
- 或检测 + 跟踪混合方案

## 运行环境补充

项目当前依赖过：

- `mss`
- `numpy`
- `Pillow`
- `ultralytics`
- `pynput`

macOS 下鼠标控制还需要：

- 给终端或对应 Python 进程开启“辅助功能/无障碍”权限

## 本次沟通中值得保留的核心判断

- 4070 级 GPU 对这个任务是够用的，但瓶颈未必在 GPU
- 当前主要瓶颈来自：
  - 屏幕采集
  - YOLO 推理
  - 控制链路
- 需要尽量避免“全屏 + 大输入尺寸 + 每帧纯检测”的路线
- 更推荐往“ROI 收窄 + 小模型 + 小输入尺寸 + 跟踪补帧”的方向演进
