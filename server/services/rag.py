# services/rag.py
# RAG 检索增强模块 — 多模态 Embedding + 余弦检索 + Prompt 增强
# AI 同学负责实现

import json
import math
import os

import httpx

# ====================================================================
# 路径 & API 配置
# ====================================================================

_KNOWLEDGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photography_knowledge.json")
_EMBEDDINGS_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photography_embeddings.json")

# Jina 多模态 Embedding API（免费额度 1000 万 Token）
JINA_API_KEY = "jina_0938c7ebd7d34fa08671ac44e8b796e7a6E0fAT8BqAXcpFQ7xcucOVuCBAh"
JINA_BASE_URL = "https://api.jina.ai/v1"

# ====================================================================
# 内部 — 知识库加载
# ====================================================================

_knowledge_cache: list[dict] | None = None
_embeddings_cache: dict[str, list[float]] | None = None


def _load_knowledge() -> list[dict]:
    global _knowledge_cache
    if _knowledge_cache is None:
        with open(_KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            _knowledge_cache = json.load(f)
    return _knowledge_cache


def _load_embeddings() -> dict[str, list[float]]:
    """加载缓存的知识库向量（纯同步，文件不存在则抛异常）"""
    global _embeddings_cache
    if _embeddings_cache is not None:
        return _embeddings_cache
    with open(_EMBEDDINGS_CACHE_PATH, "r", encoding="utf-8") as f:
        _embeddings_cache = json.load(f)
    return _embeddings_cache


# ====================================================================
# 内部 — 余弦相似度
# ====================================================================

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ====================================================================
# 内部 — Jina Embedding API
# ====================================================================

async def _embed_texts(texts: list[str]) -> list[list[float]]:
    """文本批量向量化"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{JINA_BASE_URL}/embeddings",
            headers={
                "Authorization": f"Bearer {JINA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "jina-embeddings-v4",
                "task": "retrieval.passage",
                "input": [{"text": t} for t in texts],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return [d["embedding"] for d in data["data"]]


async def _embed_image(image_b64: str) -> list[float]:
    """图片向量化 — Jina 多模态 Embedding"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{JINA_BASE_URL}/embeddings",
            headers={
                "Authorization": f"Bearer {JINA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "jina-embeddings-v4",
                "task": "retrieval.query",
                "input": [{"image": f"data:image/jpeg;base64,{image_b64}"}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]


# ====================================================================
# 公开 — 向量初始化（首次运行或知识库更新后调用一次）
# ====================================================================

async def init_embeddings() -> dict[str, list[float]]:
    """预计算知识库所有卡片的向量，缓存到本地 JSON 文件

    首次运行自动调用一次。后续知识库内容变更后，删除缓存文件再重启即可重建。
    """
    global _embeddings_cache

    # 已有缓存，直接加载
    if os.path.exists(_EMBEDDINGS_CACHE_PATH):
        return _load_embeddings()

    knowledge = _load_knowledge()
    texts = [k["text"] for k in knowledge]
    vectors = await _embed_texts(texts)

    result = {}
    for item, vec in zip(knowledge, vectors):
        result[item["id"]] = vec

    with open(_EMBEDDINGS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    _embeddings_cache = result
    return result


# ====================================================================
# 公开 — 检索 & 增强（被 deepseek.py 调用）
# ====================================================================

async def retrieve_by_embedding(image_b64: str, mode: str, max_items: int = 3) -> list[dict]:
    """多模态 RAG 检索：图片向量化 → 余弦比对知识库 → 返回 Top K

    Args:
        image_b64: JPEG base64 编码的图片
        mode: 分析模式 "shooting" / "edit" / "score"
        max_items: 返回条数

    Returns:
        最相关的知识条目列表
    """
    # 确保向量已初始化
    if not os.path.exists(_EMBEDDINGS_CACHE_PATH):
        await init_embeddings()

    knowledge = _load_knowledge()
    embeddings = _load_embeddings()

    # 图片 → 向量
    query_vec = await _embed_image(image_b64)

    # 按 mode 筛选 → 计算相似度 → 排序
    scored = []
    for item in knowledge:
        if item.get("mode") != mode:
            continue
        vec = embeddings.get(item["id"])
        if vec is None:
            continue
        scored.append((_cosine_similarity(query_vec, vec), item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:max_items]]


def augment_prompt(original_prompt: str, knowledge_items: list[dict]) -> str:
    """把检索到的知识注入原始 prompt

    Args:
        original_prompt: 原始 prompt 文本
        knowledge_items: retrieve_by_embedding 返回的知识条目

    Returns:
        增强后的 prompt
    """
    if not knowledge_items:
        return original_prompt

    lines = ["[参考知识库 — 以下摄影专业知识来自多模态语义检索，将指导你的分析和建议]\n"]

    for i, item in enumerate(knowledge_items, 1):
        topic = item.get("topic", "摄影技巧")
        text = item.get("text", "")
        lines.append(f"{i}. 【{topic}】\n   {text}\n")

    lines.append("---\n")
    return "\n".join(lines) + original_prompt
