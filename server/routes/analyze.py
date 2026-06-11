# routes/analyze.py
# POST /api/images — 上传图片，快速返回 image_id（无 AI，不会超时）
# POST /api/analyze — 接收 image_id + mode，触发 AI 分析

import uuid

from fastapi import APIRouter, UploadFile, Form
from pydantic import BaseModel

from services.photo_analysis import shooting, edit, score, AnalysisError
from services.image_store import put, pop
from utils.image import compress_to_base64, ImageError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


class AnalyzeRequest(BaseModel):
    image_id: str
    mode: str = "shooting"
    uid: str = "device_unknown"
    thumb_url: str = ""


@router.post("/api/images")
async def upload_image(file: UploadFile = None):
    """只上传+压缩，不调 AI，快速返回"""
    if file is None or not file.filename:
        return ResponseBuilder.error("图片不能为空")
    try:
        img_b64, thumb_url = await compress_to_base64(file)
    except ImageError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"图片处理失败: {e}")

    image_id = uuid.uuid4().hex
    put(image_id, img_b64)
    return ResponseBuilder.ok({"image_id": image_id, "thumb_url": thumb_url})


@router.post("/api/analyze")
async def analyze(body: AnalyzeRequest):
    """根据已上传的 image_id 触发 AI 分析"""
    if body.mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {body.mode}")

    img_b64 = pop(body.image_id)
    if img_b64 is None:
        return ResponseBuilder.error("图片已过期，请重新上传")

    try:
        result = await HANDLERS[body.mode](body.uid.strip(), img_b64, body.thumb_url)
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
