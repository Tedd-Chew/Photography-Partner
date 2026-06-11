# utils/image.py
# 图片预处理：压缩、转 base64、保存缩略图

from PIL import Image, UnidentifiedImageError
import base64
import io
import uuid
import os
from config import MAX_IMAGE_SIZE, JPEG_QUALITY

STATIC_DIR = "static"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}


class ImageError(Exception):
    """图片处理异常"""


async def compress_to_base64(upload_file) -> tuple[str, str]:
    """
    接收 UploadFile → 压缩 → 返回 (base64, thumb_url)。
    非法文件抛出 ImageError。
    """
    if upload_file.content_type and upload_file.content_type.startswith("image/") and upload_file.content_type not in ALLOWED_TYPES:
        raise ImageError(f"不支持的图片格式: {upload_file.content_type}")

    contents = await upload_file.read()
    if len(contents) == 0:
        raise ImageError("上传文件为空")

    try:
        img = Image.open(io.BytesIO(contents))
    except UnidentifiedImageError:
        raise ImageError("无法识别的图片文件")

    # 转 RGB（处理 RGBA / PNG / 调色板模式）
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    # 压缩至最长边
    w, h = img.size
    if max(w, h) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # 缩略图 200px 给 Gallery
    os.makedirs(STATIC_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    thumb = img.copy()
    tw, th = thumb.size
    if max(tw, th) > 150:
        r = 150 / max(tw, th)
        thumb = thumb.resize((int(tw * r), int(th * r)), Image.LANCZOS)
    thumb.save(os.path.join(STATIC_DIR, filename), "JPEG", quality=75)
    thumb_url = f"/static/{filename}"

    # base64 给 AI
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), thumb_url
