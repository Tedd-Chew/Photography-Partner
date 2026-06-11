# services/image_store.py
# 临时存储已压缩的 base64 图片，供两步上传-分析流程使用
# 分析完成后自动清除，防止内存泄漏

import time
import threading

_store: dict[str, tuple[str, float]] = {}  # image_id → (base64, created_at)
_lock = threading.Lock()
_TTL = 300  # 5 分钟过期


def put(image_id: str, base64: str) -> None:
    with _lock:
        _store[image_id] = (base64, time.time())
        # 清理过期条目
        expired = [k for k, v in _store.items() if time.time() - v[1] > _TTL]
        for k in expired:
            del _store[k]


def pop(image_id: str) -> str | None:
    """取出并删除，一次性使用"""
    with _lock:
        entry = _store.pop(image_id, None)
        return entry[0] if entry else None
