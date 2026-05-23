# utils/response.py
# 统一 API 响应格式


class ResponseBuilder:
    """统一构建 { ok, data, error }"""

    @staticmethod
    def ok(data=None):
        return {"ok": True, "data": data or {}}

    @staticmethod
    def error(msg: str):
        return {"ok": False, "error": msg}
