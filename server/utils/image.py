# utils/image.py
# 图片预处理：压缩、转 base64
# 传统后端（你）负责实现

from PIL import Image
import base64
import io
from config import MAX_IMAGE_SIZE, JPEG_QUALITY


async def compress_to_base64(upload_file) -> str:
    """
    接收 UploadFile → 压缩 → 返回 base64 字符串
    """
    contents = await upload_file.read()
    img = Image.open(io.BytesIO(contents))

    # 转 RGB（处理 RGBA/PNG）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 压缩至最长边 MAX_IMAGE_SIZE
    w, h = img.size
    if max(w, h) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # 输出为 JPEG bytes → base64
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
