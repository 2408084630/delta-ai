from dataclasses import dataclass, field


@dataclass(slots=True)
class RoiConfig:
    """ROI 区域配置。"""

    # 需要采集的区域宽度占目标屏幕宽度的比例。
    width_ratio: float = 0.3
    # 需要采集的区域高度占目标屏幕高度的比例。
    height_ratio: float = 0.3
    # 对 ROI 做降采样时使用的缩放比例，1.0 表示不缩放。
    downscale_factor: float = 1.0


@dataclass(slots=True)
class CaptureConfig:
    """屏幕采集配置。"""

    # 采集时使用的显示器编号。
    # `mss` 中 1 表示第一块物理屏幕，0 通常表示所有屏幕的虚拟桌面。
    monitor_index: int = 1
    # 是否强制把 ROI 锚定在屏幕中心。
    # 当前低延迟方案默认始终采集中心区域，后面如果要做自定义 ROI 可以扩展这个配置。
    center_locked: bool = True
    # 是否在初始化时预热采集 backend。
    # 预热可以减少第一帧耗时抖动，便于做性能测试。
    warmup_frames: int = 3


@dataclass(slots=True)
class RuntimeConfig:
    """主循环运行配置。"""

    # 目标循环帧率，仅用于后续持续监测模式的节流。
    target_fps: int = 60
    # 是否启用持续监测模式。
    # 为 True 时，程序会按目标帧率不断执行采集、检测、追踪与控制流程。
    continuous_mode: bool = True
    # 调试阶段最多执行多少次主循环。
    # 设为 0 表示无限循环，便于后续做常驻监测；当前默认 5 次是为了避免初次运行时直接卡在前台。
    max_ticks: int = 5
    # 为低延迟模式保留的策略。
    # 为 True 时，后续持续循环只处理最新帧，不排队消费旧帧。
    latest_frame_only: bool = True
    # 是否在主链路中打印或记录每个阶段的耗时。
    profile_pipeline: bool = True
    # 打印统计信息时使用的时间窗口大小。
    # 例如设为 30 表示每执行 30 次循环输出一次平均耗时。
    stats_window: int = 30


@dataclass(slots=True)
class DetectionConfig:
    """目标检测配置。"""

    # 检测 backend 类型。
    # 当前支持：
    # - stub: 空检测器
    # - ultralytics: 使用 ultralytics YOLO
    detector_type: str = "stub"
    # 模型权重路径。
    # 当 detector_type=ultralytics 时需要提供，例如 `models/player.pt`。
    model_path: str = ""
    # 模型输入尺寸。
    # 为了压低延迟，建议优先使用 320 或 416 这类较小尺寸。
    image_size: int = 320
    # 最低置信度阈值。
    confidence_threshold: float = 0.35
    # NMS 使用的 IoU 阈值。
    iou_threshold: float = 0.45
    # 是否优先使用 GPU。
    # 当依赖和环境可用时，会把推理设备设置为 `cuda:0`。
    prefer_gpu: bool = True
    # 限制最多保留多少个候选框。
    # 持续监测场景下通常不需要保留太多结果，减少后处理也能降低抖动。
    max_detections: int = 10
    # 需要过滤的类别编号列表。
    # 为空表示不过滤，后续如果你的模型区分敌我或人物类型，可以在这里收敛结果。
    class_ids: tuple[int, ...] = ()
    # debug detector 生成测试框时使用的标签名。
    debug_label: str = "debug_target"
    # debug detector 生成测试框时使用的置信度。
    debug_confidence: float = 0.95
    # debug detector 测试框中心点的横向比例位置。
    # 0.5 表示画面正中央。
    debug_center_x_ratio: float = 0.5
    # debug detector 测试框中心点的纵向比例位置。
    # 0.5 表示画面正中央。
    debug_center_y_ratio: float = 0.5
    # debug detector 测试框宽度占当前帧宽度的比例。
    debug_box_width_ratio: float = 0.2
    # debug detector 测试框高度占当前帧高度的比例。
    debug_box_height_ratio: float = 0.35


@dataclass(slots=True)
class InputConfig:
    """鼠标输出配置。"""

    # 鼠标 backend 类型。
    # 当前支持：
    # - stub: 空输出，不真正移动鼠标
    # - pynput: 使用 pynput 控制系统鼠标
    backend_type: str = "stub"
    # 是否真正执行鼠标移动。
    # 为 False 时，即使 backend 已经创建成功，也只会在控制层生成命令而不落地执行。
    enabled: bool = False
    # 相对检测框中心点的 x 方向偏移。
    # 单位是像素，映射到屏幕后再生效，后续可以用于准星修正。
    offset_x: int = 0
    # 相对检测框中心点的 y 方向偏移。
    offset_y: int = 0
    # 是否把最终鼠标坐标限制在当前屏幕边界内。
    # 先默认开启，避免后续参数配置错误时把鼠标甩到异常区域。
    clamp_to_screen: bool = True


@dataclass(slots=True)
class AppConfig:
    """应用总配置。"""

    # ROI 相关参数。
    roi: RoiConfig = field(default_factory=RoiConfig)
    # 屏幕采集相关参数。
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    # 检测器相关参数。
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    # 鼠标输出相关参数。
    input: InputConfig = field(default_factory=InputConfig)
    # 运行时相关参数。
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
