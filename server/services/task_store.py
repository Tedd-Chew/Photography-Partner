# services/task_store.py
# 临时存储 AI 分析任务结果，供轮询使用
# 分析完成后保留 5 分钟自动过期

import time
import threading

_store: dict[str, dict] = {}
_lock = threading.Lock()
_TTL = 300  # 5 分钟


def create(task_id: str) -> None:
    with _lock:
        _store[task_id] = {"status": "processing", "_ts": time.time()}


def complete(task_id: str, data: dict) -> None:
    with _lock:
        _store[task_id] = {"status": "done", "data": data, "_ts": time.time()}
        _cleanup()


def fail(task_id: str, error: str) -> None:
    with _lock:
        _store[task_id] = {"status": "error", "error": error, "_ts": time.time()}
        _cleanup()


def get(task_id: str) -> dict | None:
    with _lock:
        return _store.get(task_id)


def _cleanup() -> None:
    now = time.time()
    expired = [k for k, v in _store.items() if now - v.get("_ts", 0) > _TTL]
    for k in expired:
        del _store[k]
