# routes/analyze.py
# POST /api/images        — 上传图片，快速返回 image_id（无 AI，不会超时）
# POST /api/analyze       — 接收 image_id，后台执行 AI，立即返回 task_id
# GET  /api/analyze/{id}  — 轮询 AI 结果

import asyncio
import uuid

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from services.photo_analysis import shooting, edit, score, AnalysisError
from services.image_store import put, pop
from services import task_store
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
    """启动后台 AI 分析，立即返回 task_id"""
    if body.mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {body.mode}")

    img_b64 = pop(body.image_id)
    if img_b64 is None:
        return ResponseBuilder.error("图片已过期，请重新上传")

    task_id = uuid.uuid4().hex
    task_store.create(task_id)

    async def run():
        try:
            result = await HANDLERS[body.mode](body.uid.strip(), img_b64, body.thumb_url)
            task_store.complete(task_id, result)
        except AnalysisError as e:
            task_store.fail(task_id, str(e))
        except Exception as e:
            task_store.fail(task_id, f"服务器内部错误: {e}")

    asyncio.create_task(run())
    return ResponseBuilder.ok({"task_id": task_id})


@router.get("/api/analyze/{task_id}")
async def get_result(task_id: str):
    """轮询 AI 分析结果"""
    task = task_store.get(task_id)
    if task is None:
        return ResponseBuilder.error("任务不存在或已过期")
    if task["status"] == "processing":
        return ResponseBuilder.ok({"status": "processing"})
    if task["status"] == "error":
        return ResponseBuilder.error(task["error"])
    return ResponseBuilder.ok(task["data"])
