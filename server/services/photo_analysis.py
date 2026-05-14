# services/photo_analysis.py
# 照片分析业务编排

from services.deepseek import shooting_advice, editing_advice, score_photo
from models.database import save_analysis, update_user_exp, check_badge_unlock
from utils.image import compress_to_base64
from config import EXP_PER_ANALYSIS, EXP_HIGH_SCORE, EXP_PERFECT_SCORE


async def _compress(upload_file) -> tuple[str, str]:
    return await compress_to_base64(upload_file)


async def shooting(uid: str, image) -> dict:
    img_b64, thumb_url = await _compress(image)
    result = await shooting_advice(img_b64)
    result["id"] = await save_analysis(uid, "shooting", result, thumb_url)
    result["mode"] = "shooting"
    result["thumb_url"] = thumb_url
    return result


async def edit(uid: str, image) -> dict:
    """修图建议 — AI 返回纯文本"""
    img_b64, thumb_url = await _compress(image)
    advice = await editing_advice(img_b64)  # str
    result = {"advice": advice}
    result["id"] = await save_analysis(uid, "edit", result, thumb_url)
    result["mode"] = "edit"
    result["thumb_url"] = thumb_url
    return result


async def score(uid: str, image) -> dict:
    img_b64, thumb_url = await _compress(image)
    result = await score_photo(img_b64)

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
    result["id"] = await save_analysis(uid, "score", result, thumb_url)
    result["mode"] = "score"
    result["thumb_url"] = thumb_url
    return result
