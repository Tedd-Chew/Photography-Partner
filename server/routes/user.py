# routes/user.py
# 用户相关接口

from fastapi import APIRouter
from pydantic import BaseModel
from models.database import get_or_create_user, do_checkin

router = APIRouter()


class CheckinRequest(BaseModel):
    uid: str


@router.get("/api/user/info")
async def user_info(uid: str):
    """获取或创建用户"""
    user = await get_or_create_user(uid)
    return {"ok": True, "data": user}


@router.post("/api/user/checkin")
async def user_checkin(body: CheckinRequest):
    """每日打卡"""
    result = await do_checkin(body.uid)
    return {"ok": True, "data": result}
