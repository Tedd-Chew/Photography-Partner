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


# ====== 三种分析函数 ======

async def shooting_advice(image_b64: str) -> dict:
    """拍摄指导：场景+参数+构图"""
    prompt = _load_prompt("shooting.txt")
    raw = await _call_vision(prompt, image_b64, max_tokens=1024)
    return _parse_json(raw)


async def editing_advice(image_b64: str) -> dict:
    """修图建议：问题诊断+调色步骤"""
    prompt = _load_prompt("edit.txt")
    raw = await _call_vision(prompt, image_b64, max_tokens=1024)
    return _parse_json(raw)


async def score_photo(image_b64: str) -> dict:
    """评分评价：五维评分+优缺点"""
    prompt = _load_prompt("score.txt")
    raw = await _call_vision(prompt, image_b64, max_tokens=1024)
    return _parse_json(raw)
