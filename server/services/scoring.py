# services/scoring.py
# 评分、等级、勋章规则
# AI 同学负责维护

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
    "首战告捷": lambda user, result: result.get("score", 0) >= 90 and user["total_analyses"] <= 5,
    "高分达人": lambda user, result: result.get("score", 0) >= 85,
    "光影艺术家": lambda user, result: user["total_analyses"] >= 50,
}


def get_level(exp: int) -> dict:
    current = LEVELS[0]
    next_lvl = LEVELS[1] if len(LEVELS) > 1 else None
    for i, lvl in enumerate(LEVELS):
        if exp >= lvl["exp_needed"]:
            current = lvl
            next_lvl = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    exp_to_next = next_lvl["exp_needed"] - exp if next_lvl else 0
    return {**current, "exp_to_next": exp_to_next, "next_level": next_lvl}
