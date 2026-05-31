# routes/user.py
# GET /api/user/info — 获取或创建用户

from fastapi import APIRouter, Query
from models.database import get_or_create_user
from utils.response import ResponseBuilder

router = APIRouter()


@router.get("/api/user/info")
async def user_info(uid: str = Query(..., min_length=1)):
    if not uid.strip():
        return ResponseBuilder.error("uid 不能为空")
    user = await get_or_create_user(uid.strip())
    return ResponseBuilder.ok(user)
