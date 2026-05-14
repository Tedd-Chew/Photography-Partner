# routes/user.py
# 用户相关接口

from fastapi import APIRouter
from models.database import get_or_create_user

router = APIRouter()


@router.get("/api/user/info")
async def user_info(uid: str):
    """获取或创建用户"""
    return {"ok": True, "data": await get_or_create_user(uid)}
