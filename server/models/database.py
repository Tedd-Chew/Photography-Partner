import aiosqlite
import json
import uuid
from config import DB_PATH
from services.scoring import BADGES, get_level

MAX_RECORDS = 30  # 每人最多保留的分析记录数


def _open():
    return aiosqlite.connect(DB_PATH)


async def init_db():
    """建表"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                nickname TEXT DEFAULT '',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                badges_json TEXT DEFAULT '[]',
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
                thumb_url TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        """)
        await db.commit()


# ====== 用户 ======

async def get_or_create_user(uid: str) -> dict:
    """获取用户信息，不存在则创建"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
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
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT level, exp FROM users WHERE uid = ?", (uid,))
        row = await cursor.fetchone()
        old_level = row["level"]
        new_exp = row["exp"] + exp_delta
        level_data = get_level(new_exp)
        new_level = level_data["level"]
        level_up = new_level > old_level
        await db.execute(
            "UPDATE users SET exp = ?, level = ?, updated_at = datetime('now') WHERE uid = ?",
            (new_exp, new_level, uid),
        )
        await db.commit()
    return {"level_up": level_up, "old_level": old_level, "new_level": new_level}


async def check_badge_unlock(uid: str, result: dict) -> list:
    """检查新勋章，返回新勋章名列表"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT badges_json, total_analyses FROM users WHERE uid = ?", (uid,)
        )
        row = await cursor.fetchone()
        current = set(json.loads(row["badges_json"] or "[]"))
        ctx = {"total_analyses": row["total_analyses"]}
        new_badges = [n for n, r in BADGES.items()
                      if n not in current and r(ctx, result)]
        if new_badges:
            current.update(new_badges)
            await db.execute(
                "UPDATE users SET badges_json = ? WHERE uid = ?",
                (json.dumps(list(current), ensure_ascii=False), uid),
            )
            await db.commit()
    return new_badges


# ====== 分析记录 ======

async def save_analysis(uid: str, mode: str, result: dict, thumb_url: str = "") -> str:
    """保存分析记录，FIFO 30 条"""
    record_id = str(uuid.uuid4())
    async with _open() as db:
        await db.execute(
            "INSERT INTO analyses (id, uid, mode, result_json, thumb_url) VALUES (?, ?, ?, ?, ?)",
            (record_id, uid, mode, json.dumps(result, ensure_ascii=False), thumb_url),
        )
        await db.execute(
            "UPDATE users SET total_analyses = total_analyses + 1 WHERE uid = ?",
            (uid,),
        )
        await db.execute(
            "DELETE FROM analyses WHERE uid = ? AND id NOT IN ("
            "SELECT id FROM analyses WHERE uid = ? ORDER BY created_at DESC LIMIT ?)",
            (uid, uid, MAX_RECORDS),
        )
        await db.commit()
    return record_id


async def get_analyses(uid: str, page: int = 1, size: int = 20) -> dict:
    """分页查询历史"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        offset = (page - 1) * size
        cursor = await db.execute(
            "SELECT id, mode, result_json, thumb_url, created_at FROM analyses "
            "WHERE uid = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (uid, size, offset),
        )
        items = [dict(r) for r in await cursor.fetchall()]
        cursor = await db.execute(
            "SELECT COUNT(*) FROM analyses WHERE uid = ?", (uid,)
        )
        total = (await cursor.fetchone())[0]
    return {"items": items, "total": total, "page": page}


async def get_analysis_by_id(record_id: str) -> dict | None:
    """单条详情"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM analyses WHERE id = ?", (record_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_stats(uid: str) -> dict:
    """用户统计数据（Growth 页用）"""
    async with _open() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT result_json, created_at FROM analyses "
            "WHERE uid = ? AND mode = 'score' ORDER BY created_at DESC LIMIT 7",
            (uid,),
        )
        rows = await cursor.fetchall()
        scores = []
        for r in rows:
            data = json.loads(r["result_json"] or "{}")
            scores.append({
                "date": r["created_at"][:10],
                "overall": data.get("overall", 0),
            })
    return {"recent_scores": scores}
