# routes/analyze.py
# POST /api/analyze — 照片分析（三种模式）

from fastapi import APIRouter, UploadFile, Form
from services.deepseek import shooting_advice, editing_advice, score_photo
from models.database import save_analysis, get_or_create_user, update_user_exp, check_badge_unlock
from utils.image import compress_to_base64
from config import EXP_PER_ANALYSIS, EXP_HIGH_SCORE

router = APIRouter()


@router.post("/api/analyze")
async def analyze(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
    """
    照片分析 — 三种模式：
    - shooting: 拍摄指导（场景+参数+构图）
    - edit:     修图建议（问题诊断+调色步骤）
    - score:    评分评价（五维评分+优缺点）
    """
    # 1. 图片预处理
    img_b64 = await compress_to_base64(image)

    # 2. 根据 mode 调用不同 AI 函数
    if mode == "shooting":
        result = await shooting_advice(img_b64)
    elif mode == "edit":
        result = await editing_advice(img_b64)
    elif mode == "score":
        result = await score_photo(img_b64)
        # 评分才更新成长体系
        overall = result.get("overall", 0)
        exp_gained = EXP_PER_ANALYSIS
        if overall > 90:
            exp_gained += EXP_HIGH_SCORE
        elif overall > 80:
            exp_gained += EXP_HIGH_SCORE
        level_up = await update_user_exp(uid, exp_gained)
        badge = await check_badge_unlock(uid, result)
        result["exp_gained"] = exp_gained
        result["level_up"] = level_up
        result["badge_unlocked"] = badge
    else:
        return {"ok": False, "error": f"未知模式: {mode}"}

    # 3. 存入数据库
    record_id = await save_analysis(uid, mode, result)
    result["id"] = record_id
    result["mode"] = mode

    return {"ok": True, "data": result}
