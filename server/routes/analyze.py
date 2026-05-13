# routes/analyze.py
# POST /api/analyze — 接收请求，分发到业务层

from fastapi import APIRouter, UploadFile, Form
from services.photo_analysis import shooting, edit, score

router = APIRouter()

HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


@router.post("/api/analyze")
async def analyze(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
    """三种模式：shooting(拍摄指导) / edit(修图建议) / score(评分评价)"""
    if mode not in HANDLERS:
        return {"ok": False, "error": f"未知模式: {mode}"}
    result = await HANDLERS[mode](uid, image)
    return {"ok": True, "data": result}
