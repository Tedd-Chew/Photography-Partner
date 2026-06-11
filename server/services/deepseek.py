# services/deepseek.py
# DeepSeek Vision API 封装 — 三种分析模式
# AI 同学负责实现

import json
import re
import asyncio
import uuid

from openai import (
    AsyncOpenAI,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)
from config import VIVO_APP_KEY, VIVO_BASE_URL, MODEL_NAME
from schemas.response import CameraParams

# ====================================================================
# API 客户端
# ====================================================================

client = AsyncOpenAI(
    api_key=VIVO_APP_KEY,
    base_url=VIVO_BASE_URL,
    timeout=60.0,
    max_retries=0,
    default_headers={"Content-Type": "application/json; charset=utf-8"},
    default_query={"request_id": str(uuid.uuid4())},
)

_RETRYABLE = (APITimeoutError, APIConnectionError, InternalServerError, RateLimitError)


# ====================================================================
# 内部工具函数
# ====================================================================

def _load_prompt(filename: str) -> str:
    """加载 prompt 模板文件"""
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def _parse_json(raw: str) -> dict:
    """解析 AI 返回的 JSON — 四级兜底，绝不抛异常

    第 1 级：去掉 ```json 包裹 → 直接 json.loads
    第 2 级：正则提取 { 到 } 片段 → 再试 json.loads
    第 3 级：彻底失败 → 返回 {"_parse_failed": True}
    """
    if not raw or not isinstance(raw, str):
        return {"_parse_failed": True, "_raw": str(raw)[:500]}

    # 第 1 级：清理 markdown 包裹
    cleaned = re.sub(r'^```json?\s*', '', raw.strip())
    cleaned = re.sub(r'\s*```$', '', cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 第 2 级：正则提取大括号片段
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 第 3 级：兜底
    return {"_parse_failed": True, "_raw": raw[:500]}


async def _call_vision(prompt: str, image_b64: str, max_tokens: int = 1024) -> str:
    """调用 vivo Vision API — 30s 超时 + 智能重试（可重试错误重试 1 次）"""
    last_error = None

    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }}
                    ]
                }],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            # content 理论上不会是 None，但防御性处理
            content = response.choices[0].message.content
            return content if content else ""
        except _RETRYABLE as e:
            last_error = e
            if attempt == 0:
                await asyncio.sleep(1)
        # 不可重试错误（401/400 等）直接向上抛

    raise last_error


def _validate_field(data: dict, key: str, pydantic_model):
    """用 Pydantic 模型校验 data[key]，字段缺失则跳过"""
    if key in data:
        val = data[key]
        if isinstance(val, list):
            for item in val:
                pydantic_model.model_validate(item)
        else:
            pydantic_model.model_validate(val)


# ====================================================================
# 公开函数 — 被 photo_analysis.py 调用
# 合约：函数名 / 参数 (image_b64: str) / 返回值类型 不可变
# ====================================================================

async def shooting_advice(image_b64: str) -> dict:
    """拍摄指导：分析照片 → 返回场景、快门/ISO/WB、构图建议等

    返回值示例：
        {
          "scene": "夜景人像",
          "camera_params": { "shutter": "1/30", "iso": "800", ... },
          "composition_tips": ["人物置于右侧三分线", ...],
          "lighting_advice": "利用街道暖色灯光...",
          "extra_tips": "建议使用三脚架"
        }
    解析失败时返回"请重试"占位结构，不抛异常。
    """
    raw = await _call_vision(_load_prompt("shooting.txt"), image_b64)
    data = _parse_json(raw)

    if data.get("_parse_failed"):
        return {
            "scene": "识别失败",
            "camera_params": {
                "shutter": "请重试", "iso": "请重试",
                "aperture": "请重试", "wb": "请重试", "focus": "请重试",
            },
            "composition_tips": ["AI 返回异常，请稍后重试"],
            "lighting_advice": "请稍后重试",
            "extra_tips": "请稍后重试",
        }

    _validate_field(data, "camera_params", CameraParams)
    return data


async def editing_advice(image_b64: str) -> str:
    """修图建议：分析照片 → 返回纯文本修图指导（约 200 字）

    不走 JSON 解析，AI 直接输出自然语言。
    网络/API 异常会向上抛，由 photo_analysis 层兜底。
    """
    return await _call_vision(_load_prompt("edit.txt"), image_b64)


async def score_photo(image_b64: str) -> dict:
    """评分评价：分析照片 → 返回 { "score": 0-100, "comment": "评语" }

    score 保证是 0-100 的整数，comment 保证是字符串。
    解析失败或 AI 返回非法 score 值时有安全兜底，不抛异常。
    """
    raw = await _call_vision(_load_prompt("score.txt"), image_b64)
    data = _parse_json(raw)

    if data.get("_parse_failed"):
        return {"score": 0, "comment": "AI 返回异常，请稍后重试"}

    # 提取并清洗 score
    score = data.get("score", 0)
    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0
    score = max(0, min(100, score))

    # 提取并清洗 comment
    comment = data.get("comment")
    if not isinstance(comment, str):
        comment = str(comment) if comment is not None else ""

    return {"score": score, "comment": comment}
