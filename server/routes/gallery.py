# routes/gallery.py
# 历史记录接口

from fastapi import APIRouter
from models.database import get_analyses, get_analysis_by_id

router = APIRouter()


@router.get("/api/gallery")
async def gallery_list(uid: str, page: int = 1, size: int = 20):
    """历史分析记录列表"""
    result = await get_analyses(uid, page, size)
    return {"ok": True, "data": result}


@router.get("/api/gallery/{record_id}")
async def gallery_detail(record_id: str):
    """单条分析详情"""
    record = await get_analysis_by_id(record_id)
    if record:
        return {"ok": True, "data": record}
    return {"ok": False, "error": "记录不存在"}
