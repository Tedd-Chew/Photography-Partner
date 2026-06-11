# routes/analyze.py
# POST /api/analyze — 接收 uploadtask multipart（字段名: file）

from fastapi import APIRouter, UploadFile, Form
from services.photo_analysis import shooting, edit, score, AnalysisError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


@router.post("/api/analyze")
async def analyze(
    file: UploadFile = None,
    mode: str = Form(default="shooting"),
    uid: str = Form(default="device_unknown")
):
    if file is None or not file.filename:
        return ResponseBuilder.error("图片不能为空")
    if mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {mode}")
    try:
        result = await HANDLERS[mode](uid.strip(), file)
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
