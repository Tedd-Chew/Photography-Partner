# utils/response.py
# 统一响应格式（预留）
# 当前在路由里直接 return {"ok": ..., "data": ...}


def ok(data):
    return {"ok": True, "data": data}


def error(msg):
    return {"ok": False, "error": msg}
