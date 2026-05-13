# routes/scene.py
# POST /api/scene/detect — 场景检测 + 参数推荐

from fastapi import APIRouter, UploadFile, Form
from services.deepseek import detect_scene
from utils.image import compress_to_base64

router = APIRouter()


@router.post("/api/scene/detect")
async def scene_detect(image: UploadFile):
    """Camera 页调用：低分辨率预览帧 → 场景+推荐参数"""
    img_b64 = await compress_to_base64(image)
    result = await detect_scene(img_b64)
    return {"ok": True, "data": result}
