# routes/analyze.py
# POST /api/analyze — 照片分析，三种模式
# 支持 multipart/form-data 和 raw binary body

from fastapi import APIRouter, UploadFile, Form, Request
from services.photo_analysis import shooting, edit, score, AnalysisError
from utils.response import ResponseBuilder

router = APIRouter()
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}


class RawImageFile:
    """用 raw bytes 构造兼容 UploadFile 的对象"""
    def __init__(self, data: bytes):
        self.filename = "photo.jpg"
        self.content_type = "image/jpeg"
        self._data = data

    async def read(self):
        return self._data


@router.post("/api/analyze")
async def analyze(request: Request):
    content_type = request.headers.get("content-type", "")
    print(f"[analyze] content-type={content_type}")

    # multipart/form-data
    if "multipart" in content_type:
        form = await request.form()
        print(f"[analyze] form keys={list(form.keys())}")
        for k, v in form.items():
            print(f"[analyze]   {k}={type(v).__name__} filename={getattr(v,'filename','N/A')}")
        image = form.get("file") or form.get("image")
        mode = form.get("mode")
        uid = form.get("uid")
        if not image or not hasattr(image, 'filename'):
            return ResponseBuilder.error("图片不能为空")
        upload_file = image
    else:
        # 尝试从 body 读 raw bytes，参数从 query string 取
        body = await request.body()
        if not body:
            return ResponseBuilder.error("图片不能为空")
        mode = request.query_params.get("mode", "")
        uid = request.query_params.get("uid", "")
        upload_file = RawImageFile(body)

    if not uid or not str(uid).strip():
        return ResponseBuilder.error("uid 不能为空")
    if mode not in HANDLERS:
        return ResponseBuilder.error(f"未知模式: {mode}")

    try:
        result = await HANDLERS[mode](str(uid).strip(), upload_file)
        return ResponseBuilder.ok(result)
    except AnalysisError as e:
        return ResponseBuilder.error(str(e))
    except Exception as e:
        return ResponseBuilder.error(f"服务器内部错误: {e}")
