# server/schemas/response.py
# 数据契约：前端与后端的唯一接口协议。字段名不得随意变更。

from pydantic import BaseModel, Field
from typing import Optional


# ==============================================
# 统一外层响应
# ==============================================

class ApiResponse(BaseModel):
    """所有接口统一返回此结构"""
    ok: bool
    data: Optional[dict] = Field(default=None, description="成功时的业务数据")
    error: Optional[str] = Field(default=None, description="失败时的错误信息")


# ==============================================
# 模式一：拍摄指导
# ==============================================

class CameraParams(BaseModel):
    shutter: str = Field(description="建议快门速度，如 1/125")
    iso: str = Field(description="建议 ISO，如 400")
    aperture: str = Field(description="建议光圈，如 f/2.8")
    wb: str = Field(description="建议白平衡，如 5500K")
    focus: str = Field(description="对焦建议，如 人物面部单点对焦")


class ShootingData(BaseModel):
    """POST /api/analyze mode=shooting 返回的 data"""
    id: str
    mode: str = "shooting"
    thumb_url: str
    scene: str = Field(description="场景类型：人像/夜景/风景/美食/街拍/静物")
    camera_params: CameraParams
    composition_tips: list[str] = Field(description="构图建议，2-3 条")
    lighting_advice: str = Field(description="用光建议")
    extra_tips: str = Field(description="其他建议，如三脚架、闪光灯等")


# ==============================================
# 模式二：修图建议
# ==============================================

class EditData(BaseModel):
    """POST /api/analyze mode=edit 返回的 data — AI 纯文本建议"""
    id: str
    mode: str = "edit"
    thumb_url: str
    advice: str = Field(description="AI 修图建议纯文本，前端原样展示")


# ==============================================
# 模式三：评分评价
# ==============================================

class Scores(BaseModel):
    composition: int = Field(ge=0, le=100, description="构图 0-100")
    exposure: int = Field(ge=0, le=100, description="曝光 0-100")
    color: int = Field(ge=0, le=100, description="色彩 0-100")
    sharpness: int = Field(ge=0, le=100, description="清晰度 0-100")
    creativity: int = Field(ge=0, le=100, description="创意 0-100")


class LevelUpResult(BaseModel):
    level_up: bool
    old_level: int
    new_level: int


class ScoreData(BaseModel):
    """POST /api/analyze mode=score 返回的 data"""
    id: str
    mode: str = "score"
    thumb_url: str
    scores: Scores
    overall: int = Field(ge=0, le=100, description="综合评分 0-100")
    rating_label: str = Field(description="优秀/良好/一般/需改进")
    summary: str = Field(description="总体评价")
    strengths: list[str] = Field(description="优点，2-3 条")
    weaknesses: list[str] = Field(description="缺点，2-3 条")
    exp_gained: int = Field(default=0, description="本次获得的经验值")
    level_up: Optional[LevelUpResult] = Field(default=None, description="升级信息")
    badge_unlocked: Optional[list[str]] = Field(default=None, description="新解锁的勋章名")


# ==============================================
# 通用：用户信息
# ==============================================

class UserInfoData(BaseModel):
    """GET /api/user/info 返回的 data"""
    uid: str
    nickname: str = ""
    level: int = Field(ge=1, le=6, description="等级 1-6")
    exp: int = Field(ge=0, description="总经验值")
    badges: list[str] = Field(default_factory=list, description="已获勋章列表")
    total_analyses: int = Field(default=0, description="累计分析次数")


# ==============================================
# 通用：画廊历史
# ==============================================

class GalleryItem(BaseModel):
    id: str
    mode: str
    thumb_url: str
    result_json: dict = Field(description="完整的分析结果")
    created_at: str


class GalleryListData(BaseModel):
    items: list[GalleryItem]
    total: int
    page: int
