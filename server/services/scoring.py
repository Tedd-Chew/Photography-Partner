# services/scoring.py
# 评分、等级、勋章规则
# AI 同学负责维护

# ====================================================================
# 等级体系（6 级）
# ====================================================================

LEVELS = [
    {"level": 1, "name": "摄影新手",   "exp_needed": 0},
    {"level": 2, "name": "摄影学徒",   "exp_needed": 100},
    {"level": 3, "name": "摄影达人",   "exp_needed": 300},
    {"level": 4, "name": "摄影专家",   "exp_needed": 600},
    {"level": 5, "name": "摄影大师",   "exp_needed": 1000},
    {"level": 6, "name": "光影艺术家", "exp_needed": 1600},
]

# ====================================================================
# 勋章规则
#
# 每个勋章是一个 lambda：(user_ctx, result) -> bool
#   user_ctx:  {"total_analyses": int}  — 当前累计分析次数（本次尚未计入）
#   result:    {"score": int, "comment": str}  — score_photo 的返回值
#
# 注意：check_badge_unlock 在 save_analysis 之前执行，
#       所以 user_ctx["total_analyses"] 是本次分析之前的数值。
#       这意味着：
#       - "首战告捷" 用 <=4 表示"前 5 次内"（因为第 5 次分析时读数为 4）
#       - "光影艺术家" 用 >=49 表示"累计 50 次"（因为第 50 次时读数为 49）
# ====================================================================

BADGES = {
    # 前 5 次分析内拿到 ≥90 分
    "首战告捷": lambda ctx, result: (
        result.get("score", 0) >= 90 and ctx["total_analyses"] <= 4
    ),

    # 任意一次分析拿到 ≥85 分
    "高分达人": lambda ctx, result: (
        result.get("score", 0) >= 85
    ),

    # 累计分析满 50 次
    "光影艺术家": lambda ctx, result: (
        ctx["total_analyses"] >= 49
    ),
}


# ====================================================================
# 等级计算
# ====================================================================

def get_level(exp: int) -> dict:
    """根据经验值计算当前等级和距离下一级的信息

    返回示例：
        {"level": 3, "name": "摄影达人", "exp_needed": 300,
         "exp_to_next": 150, "next_level": {"level": 4, "name": "摄影专家", "exp_needed": 600}}
    """
    current = LEVELS[0]
    next_lvl = LEVELS[1] if len(LEVELS) > 1 else None

    for i, lvl in enumerate(LEVELS):
        if exp >= lvl["exp_needed"]:
            current = lvl
            next_lvl = LEVELS[i + 1] if i + 1 < len(LEVELS) else None

    exp_to_next = next_lvl["exp_needed"] - exp if next_lvl else 0

    return {
        **current,
        "exp_to_next": exp_to_next,
        "next_level": dict(next_lvl) if next_lvl else None,  # 返回副本，避免外部误改原始数据
    }
