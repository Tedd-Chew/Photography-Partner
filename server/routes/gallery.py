# routes/gallery.py
# GET /api/gallery — 历史记录

from fastapi import APIRouter, Query
from models.database import get_analyses, get_analysis_by_id
from utils.response import ResponseBuilder

router = APIRouter()


@router.get("/api/gallery")
async def gallery_list(
    uid: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=30),
):
    if not uid.strip():
        return ResponseBuilder.error("uid 不能为空")
    result = await get_analyses(uid.strip(), page, size)
    return ResponseBuilder.ok(result)


@router.get("/api/gallery/{record_id}")
async def gallery_detail(record_id: str):
    record = await get_analysis_by_id(record_id)
    if record:
        return ResponseBuilder.ok(record)
    return ResponseBuilder.error("记录不存在")
