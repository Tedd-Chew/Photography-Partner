# services/scoring.py
# 评分计算、经验规则、勋章判定
# AI 同学负责实现

# 五维权重
WEIGHTS = {
    "composition": 0.3,
    "exposure": 0.25,
    "color": 0.2,
    "sharpness": 0.15,
    "creativity": 0.1
}

# 等级体系
LEVELS = [
    {"level": 1, "name": "摄影新手", "exp_needed": 0},
    {"level": 2, "name": "摄影学徒", "exp_needed": 100},
    {"level": 3, "name": "摄影达人", "exp_needed": 300},
    {"level": 4, "name": "摄影专家", "exp_needed": 600},
    {"level": 5, "name": "摄影大师", "exp_needed": 1000},
    {"level": 6, "name": "光影艺术家", "exp_needed": 1600},
]

# 勋章规则
BADGES = {
    "首战告捷": lambda user, result: result.get("overall", 0) >= 90 and user["total_analyses"] <= 5,
    "构图大师": lambda user, result: result.get("scores", {}).get("composition", 0) >= 90,
    "色彩诗人": lambda user, result: result.get("scores", {}).get("color", 0) >= 90,
}


def calculate_overall(scores: dict) -> int:
    """加权综合分"""
    total = sum(scores.get(k, 70) * v for k, v in WEIGHTS.items())
    return round(total)


def get_level(exp: int) -> dict:
    """根据经验值返回等级信息"""
    current = LEVELS[0]
    next_lvl = LEVELS[1] if len(LEVELS) > 1 else None
    for i, lvl in enumerate(LEVELS):
        if exp >= lvl["exp_needed"]:
            current = lvl
            next_lvl = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    exp_to_next = next_lvl["exp_needed"] - exp if next_lvl else 0
    return {**current, "exp_to_next": exp_to_next, "next_level": next_lvl}


def calculate_exp_for_checkin(streak: int) -> int:
    """打卡经验"""
    return min(5 + streak * 2, 15)
