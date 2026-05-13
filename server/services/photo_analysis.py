# services/photo_analysis.py
# 照片分析业务编排 — 衔接 routes（HTTP）和 models（数据库）
# 传统后端（你）负责实现

from services.deepseek import shooting_advice, editing_advice, score_photo
from models.database import save_analysis, update_user_exp, check_badge_unlock
from utils.image import compress_to_base64
from config import EXP_PER_ANALYSIS, EXP_HIGH_SCORE, EXP_PERFECT_SCORE


async def shooting(uid: str, image) -> dict:
    """拍摄指导全流程：压缩 → AI → 存库 → 返回"""
    img_b64 = await compress_to_base64(image)
    result = await shooting_advice(img_b64)# ai调用
    result["id"] = await save_analysis(uid, "shooting", result)
    result["mode"] = "shooting"
    return result


async def edit(uid: str, image) -> dict:
    """修图建议全流程：压缩 → AI → 存库 → 返回"""
    img_b64 = await compress_to_base64(image)
    result = await editing_advice(img_b64)# ai 调用
    result["id"] = await save_analysis(uid, "edit", result)
    result["mode"] = "edit"
    return result


async def score(uid: str, image) -> dict:
    """评分评价全流程：压缩 → AI → 计算经验 → 更新等级 → 查勋章 → 存库 → 返回"""
    img_b64 = await compress_to_base64(image)
    result = await score_photo(img_b64)#ai调用

    overall = result.get("overall", 0)
    exp_gained = EXP_PER_ANALYSIS
    if overall >= 90:
        exp_gained += EXP_PERFECT_SCORE
    elif overall >= 80:
        exp_gained += EXP_HIGH_SCORE

    level_result = await update_user_exp(uid, exp_gained)
    badge = await check_badge_unlock(uid, result)

    result["exp_gained"] = exp_gained
    result["level_up"] = level_result
    result["badge_unlocked"] = badge
    result["id"] = await save_analysis(uid, "score", result)
    result["mode"] = "score"
    return result
