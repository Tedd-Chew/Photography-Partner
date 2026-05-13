# utils/image.py
# 图片预处理：压缩、转 base64、保存缩略图

from PIL import Image
import base64
import io
import uuid
import os
from config import MAX_IMAGE_SIZE, JPEG_QUALITY

STATIC_DIR = "static"


async def compress_to_base64(upload_file) -> tuple[str, str]:
    """
    接收 UploadFile → 压缩 → 返回 (base64, thumb_url)
    """
    contents = await upload_file.read()
    img = Image.open(io.BytesIO(contents))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # 保存缩略图
    os.makedirs(STATIC_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    img.save(os.path.join(STATIC_DIR, filename), "JPEG", quality=JPEG_QUALITY)
    thumb_url = f"/static/{filename}"

    # base64 给 AI 调用
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), thumb_url
