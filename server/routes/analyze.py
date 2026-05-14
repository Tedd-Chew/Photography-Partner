# routes/analyze.py
# POST /api/analyze — 接收请求，分发到业务层

from fastapi import APIRouter, UploadFile, Form
from services.photo_analysis import shooting, edit, score

router = APIRouter()

HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


@router.post("/api/analyze")
async def analyze(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
    """
    照片分析 — 三种模式。
    成功返回 { ok: true, data: ShootingData | EditData | ScoreData }
    失败返回 { ok: false, error: string }
    """
    if mode not in HANDLERS:
        return {"ok": False, "error": f"未知模式: {mode}"}
    return {"ok": True, "data": await HANDLERS[mode](uid, image)}
