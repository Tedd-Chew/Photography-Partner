# models/database.py
# SQLite 连接 + 表初始化 + CRUD 函数
# 传统后端（你）负责实现

import aiosqlite
import json
import uuid
from config import DB_PATH


async def get_db():
    """获取数据库连接"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """建表"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                nickname TEXT DEFAULT '',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                badges_json TEXT DEFAULT '[]',
                streak INTEGER DEFAULT 0,
                last_checkin TEXT,
                total_analyses INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                uid TEXT NOT NULL,
                mode TEXT NOT NULL,
                result_json TEXT,
                image_path TEXT,
                thumb_path TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                date TEXT NOT NULL,
                exp_gained INTEGER DEFAULT 0,
                FOREIGN KEY (uid) REFERENCES users(uid),
                UNIQUE(uid, date)
            )
        """)
        await db.commit()


# ====== 用户相关 ======

async def get_or_create_user(uid: str) -> dict:
    """获取用户信息，不存在则创建"""
    db = await get_db()
    async with db:
        cursor = await db.execute("SELECT * FROM users WHERE uid = ?", (uid,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        await db.execute("INSERT INTO users (uid) VALUES (?)", (uid,))
        await db.commit()
        cursor = await db.execute("SELECT * FROM users WHERE uid = ?", (uid,))
        return dict(await cursor.fetchone())


async def update_user_exp(uid: str, exp_delta: int) -> dict:
    """增加经验，检查升级"""
    # TODO: 实现经验更新 + 等级判定
    return {"level_up": False, "new_level": 1}


async def check_badge_unlock(uid: str, result: dict) -> list:
    """检查是否解锁新勋章"""
    # TODO: 实现勋章判定逻辑
    return []


async def do_checkin(uid: str) -> dict:
    """每日打卡"""
    # TODO: 实现打卡逻辑（连续/断签/今日已打）
    return {"streak": 1, "exp_gained": 5}


# ====== 分析记录 ======

async def save_analysis(uid: str, mode: str, result: dict) -> str:
    """保存分析记录，返回记录 ID"""
    record_id = str(uuid.uuid4())
    db = await get_db()
    async with db:
        await db.execute(
            "INSERT INTO analyses (id, uid, mode, result_json) VALUES (?, ?, ?, ?)",
            (record_id, uid, mode, json.dumps(result, ensure_ascii=False))
        )
        await db.commit()
    return record_id


async def get_analyses(uid: str, page: int = 1, size: int = 20) -> dict:
    """分页查询历史记录"""
    db = await get_db()
    async with db:
        offset = (page - 1) * size
        cursor = await db.execute(
            "SELECT id, mode, result_json, created_at FROM analyses WHERE uid = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (uid, size, offset)
        )
        rows = await cursor.fetchall()
        items = [dict(r) for r in rows]
        cursor = await db.execute(
            "SELECT COUNT(*) FROM analyses WHERE uid = ?", (uid,)
        )
        total = (await cursor.fetchone())[0]
    return {"items": items, "total": total, "page": page}


async def get_analysis_by_id(record_id: str) -> dict | None:
    """单条记录详情"""
    db = await get_db()
    async with db:
        cursor = await db.execute("SELECT * FROM analyses WHERE id = ?", (record_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
