# services/composition.py
# 本地构图规则引擎 — 补充 DeepSeek 的构图分析
# AI 同学负责实现

def detect_horizon_tilt(image_path: str) -> float:
    """检测水平线倾斜角度（度）"""
    # TODO: 用 OpenCV/Pillow 分析边缘
    return 0.0


def detect_subject_position(image_path: str) -> str:
    """检测主体位置: 'left' | 'center' | 'right'"""
    # TODO: 分析视觉重心
    return "center"


def evaluate_symmetry(image_path: str) -> float:
    """评估画面对称性 0-1"""
    # TODO: 水平翻转后对比
    return 0.0
