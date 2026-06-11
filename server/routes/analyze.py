# routes/analyze.py
# POST /api/analyze — 接收 JSON base64，跨平台兼容

import base64
from fastapi import APIRouter
from pydantic import BaseModel, Field
from services.photo_analysis import shooting, edit, score, AnalysisError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


class AnalyzeRequest(BaseModel):
    image: str = Field(..., description="base64 编码的照片数据")
    mode: str = Field(default="shooting", description="shooting|edit|score")
    uid: str = Field(default="device_unknown", description="设备 ID")


class Base64File:
    def __init__(self, b64: str):
        self.filename = "photo.jpg"
        self.content_type = "image/jpeg"
        self._data = base64.b64decode(b64)

    async def read(self):
        return self._data


@router.post("/api/analyze")
async def analyze(body: AnalyzeRequest):
    if not body.image:
        return ResponseBuilder.error("图片不能为空")
    if body.mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {body.mode}")
    try:
        result = await HANDLERS[body.mode](body.uid.strip(), Base64File(body.image))
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
