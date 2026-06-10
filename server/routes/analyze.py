# routes/analyze.py
# POST /api/analyze — 照片分析，三种模式

from fastapi import APIRouter, UploadFile, Form
from services.photo_analysis import shooting, edit, score, AnalysisError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


@router.post("/api/analyze")
async def analyze(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
    if not uid or not uid.strip():
        return ResponseBuilder.error("uid 不能为空")
    if not image or not image.filename:
        return ResponseBuilder.error("图片不能为空")
    if mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {mode}")
    try:
        result = await HANDLERS[mode](uid.strip(), image)
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
