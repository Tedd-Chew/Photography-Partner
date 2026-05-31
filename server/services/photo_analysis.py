# services/photo_analysis.py
# 照片分析业务编排

from services.deepseek import shooting_advice, editing_advice, score_photo
from models.database import save_analysis, update_user_exp, check_badge_unlock
from utils.image import compress_to_base64, ImageError
from config import EXP_PER_ANALYSIS, EXP_HIGH_SCORE, EXP_PERFECT_SCORE


class AnalysisError(Exception):
    """业务分析异常"""


async def _compress(upload_file) -> tuple[str, str]:
    """图片压缩，失败抛 AnalysisError"""
    try:
        return await compress_to_base64(upload_file)
    except ImageError as e:
        raise AnalysisError(str(e))
    except Exception as e:
        raise AnalysisError(f"图片处理失败: {e}")


async def shooting(uid: str, image) -> dict:
    """拍摄指导：压缩 → AI → 存库 → 返回"""
    img_b64, thumb_url = await _compress(image)
    try:
        result = await shooting_advice(img_b64)
    except Exception as e:
        raise AnalysisError(f"AI 分析失败 (shooting): {e}")
    result["id"] = await save_analysis(uid, "shooting", result, thumb_url)
    result["mode"] = "shooting"
    result["thumb_url"] = thumb_url
    return result


async def edit(uid: str, image) -> dict:
    """修图建议：压缩 → AI 纯文本 → 存库 → 返回"""
    img_b64, thumb_url = await _compress(image)
    try:
        advice = await editing_advice(img_b64)
    except Exception as e:
        raise AnalysisError(f"AI 分析失败 (edit): {e}")
    result = {"advice": advice}
    result["id"] = await save_analysis(uid, "edit", result, thumb_url)
    result["mode"] = "edit"
    result["thumb_url"] = thumb_url
    return result


async def score(uid: str, image) -> dict:
    """评分评价：压缩 → AI → 经验 → 勋章 → 存库 → 返回"""
    img_b64, thumb_url = await _compress(image)
    try:
        result = await score_photo(img_b64)
    except Exception as e:
        raise AnalysisError(f"AI 分析失败 (score): {e}")

    score_val = result.get("score", 0)
    exp_gained = EXP_PER_ANALYSIS
    if score_val >= 90:
        exp_gained += EXP_PERFECT_SCORE
    elif score_val >= 80:
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
