# routes/analyze.py
# POST /api/analyze — 照片分析，三种模式
# 支持两种格式：multipart/form-data 和 application/json(base64)

import base64
import io
from fastapi import APIRouter, UploadFile, Form
from pydantic import BaseModel, Field
from services.photo_analysis import shooting, edit, score, AnalysisError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


class AnalyzeJsonBody(BaseModel):
    image: str = Field(..., description="base64 编码的图片")
    mode: str = Field(..., description="shooting|edit|score")
    uid: str = Field(..., description="设备 ID")


class FakeUploadFile:
    """用 base64 构造一个兼容 UploadFile 的对象"""
    def __init__(self, b64: str):
        self.filename = "photo.jpg"
        self.content_type = "image/jpeg"
        self._data = base64.b64decode(b64)

    async def read(self):
        return self._data


# 原 multipart 端点（保留兼容）
@router.post("/api/analyze/multipart")
async def analyze_multipart(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
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


# 新 JSON base64 端点
@router.post("/api/analyze")
async def analyze_json(body: AnalyzeJsonBody):
    if not body.uid or not body.uid.strip():
        return ResponseBuilder.error("uid 不能为空")
    if not body.image:
        return ResponseBuilder.error("图片不能为空")
    if body.mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {body.mode}")
    try:
        fake_file = FakeUploadFile(body.image)
        result = await HANDLERS[body.mode](body.uid.strip(), fake_file)
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
