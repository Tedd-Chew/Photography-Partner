# services/deepseek.py
# DeepSeek Vision API 封装 — 三种分析模式 + 场景检测
# AI 同学负责实现

from openai import OpenAI
import json
import re
from config import VIVO_APP_KEY, VIVO_BASE_URL, MODEL_NAME

client = OpenAI(api_key=VIVO_APP_KEY, base_url=VIVO_BASE_URL)


def _load_prompt(filename):
    """加载 prompt 模板"""
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def _parse_json(raw: str) -> dict:
    """解析 AI 返回的 JSON，容错处理"""
    # 去除可能的 markdown 包裹
    raw = re.sub(r'^```json?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


async def _call_vision(prompt: str, image_b64: str, max_tokens=1024) -> str:
    """通用视觉调用"""
    response = client.chat.completions.create(
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
    return response.choices[0].message.content


# ====== 三种分析函数（返回 dict，AI 字段已通过 Pydantic 校验） ======
# id / thumb_url / exp_gained 等由 photo_analysis 层补充

from schemas.response import CameraParams


def _check(data: dict, key: str, model_class):
    """校验 data[key] 符合 Pydantic 模型。AI 返回不合法 → 立刻报错。"""
    if key in data:
        if isinstance(data[key], list):
            for item in data[key]:
                model_class.model_validate(item)
        else:
            model_class.model_validate(data[key])


async def shooting_advice(image_b64: str) -> dict:
    """拍摄指导 → 返回快门/ISO/构图等（ShootingData 核心字段）"""
    prompt = _load_prompt("shooting.txt")
    raw = await _call_vision(prompt, image_b64, max_tokens=1024)
    data = _parse_json(raw)
    _check(data, "camera_params", CameraParams)
    return data


async def editing_advice(image_b64: str) -> str:
    """修图建议 → 返回 AI 纯文本"""
    prompt = _load_prompt("edit.txt")
    return await _call_vision(prompt, image_b64, max_tokens=1024)


async def score_photo(image_b64: str) -> dict:
    """评分评价 → 返回 { score, comment }"""
    prompt = _load_prompt("score.txt")
    raw = await _call_vision(prompt, image_b64, max_tokens=512)
    data = _parse_json(raw)
    return data
