import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import aiosqlite


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    points INTEGER NOT NULL DEFAULT 0,
    daily_time TEXT,
    daily_enabled INTEGER NOT NULL DEFAULT 1,
    timezone TEXT,
    last_daily_sent DATE
);

CREATE TABLE IF NOT EXISTS categories (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS practices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code TEXT NOT NULL REFERENCES categories(code) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    steps_json TEXT,
    timer_seconds INTEGER,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    state TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_practice_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    practice_id INTEGER NOT NULL REFERENCES practices(id) ON DELETE CASCADE,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checklists (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_code TEXT NOT NULL REFERENCES checklists(code) ON DELETE CASCADE,
    title TEXT NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_checklist_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    checklist_item_id INTEGER NOT NULL REFERENCES checklist_items(id) ON DELETE CASCADE,
    done INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, checklist_item_id)
);

CREATE TABLE IF NOT EXISTS achievements (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_code TEXT NOT NULL REFERENCES achievements(code) ON DELETE CASCADE,
    earned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_code)
);
"""


SEED_JSON = {
    "categories": [
        {"code": "body", "title": "Тело"},
        {"code": "emotion", "title": "Эмоции"},
        {"code": "mind", "title": "Мышление"},
        {"code": "attention", "title": "Внимание"},
    ],
    "practices": [
        {
            "category_code": "body",
            "title": "Проверка тела",
            "description": "Короткая пауза для сканирования ощущений в теле.",
            "steps": [
                "Сядьте удобно и закройте глаза.",
                "Отметьте точки напряжения: шея, плечи, челюсть.",
                "Сделайте 3 спокойных вдоха и выдоха.",
            ],
            "timer_seconds": 60,
        },
        {
            "category_code": "emotion",
            "title": "Назови чувство",
            "description": "Отметьте и назовите текущее чувство без оценки.",
            "steps": [
                "Остановитесь на минуту.",
                "Спросите себя: что я чувствую?",
                "Назовите чувство и где оно в теле.",
            ],
            "timer_seconds": 60,
        },
        {
            "category_code": "attention",
            "title": "Пять ощущений",
            "description": "Заземление через органы чувств: 5-4-3-2-1.",
            "steps": [
                "5 вещей, которые видите.",
                "4, которые можете потрогать.",
                "3, которые слышите.",
                "2, которые чувствуете запахом.",
                "1 вкус.",
            ],
            "timer_seconds": 90,
        },
    ],
    "checklists": [
        {
            "code": "grounding",
            "title": "Заземление",
            "items": [
                "Почувствовать стопы",
                "Расслабить плечи",
                "Сделать глубокий вдох",
            ],
        },
    ],
    "achievements": [
        {"code": "streak_7", "title": "7 дней подряд", "description": "Практики 7 дней без пропусков"},
        {"code": "first_journal", "title": "Первая запись", "description": "Сделана первая запись в дневнике"},
    ],
}


class Database:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    @property
    def path(self) -> str:
        return self._db_path

    async def connect(self) -> aiosqlite.Connection:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self._db_path)
            await self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.row_factory = aiosqlite.Row
        return self._conn

    async def init(self) -> None:
        conn = await self.connect()
        await conn.executescript(SCHEMA_SQL)
        await self._seed()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def _seed(self) -> None:
        conn = await self.connect()
        # categories
        for c in SEED_JSON["categories"]:
            await conn.execute(
                "INSERT OR IGNORE INTO categories(code, title) VALUES(?, ?)",
                (c["code"], c["title"]),
            )
        # achievements
        for a in SEED_JSON["achievements"]:
            await conn.execute(
                "INSERT OR IGNORE INTO achievements(code, title, description) VALUES(?, ?, ?)",
                (a["code"], a["title"], a.get("description")),
            )
        # practices
        for p in SEED_JSON["practices"]:
            steps_json = json.dumps(p.get("steps", []), ensure_ascii=False)
            await conn.execute(
                (
                    "INSERT INTO practices(category_code, title, description, steps_json, timer_seconds, is_active)\n"
                    "SELECT ?, ?, ?, ?, ?, 1\n"
                    "WHERE NOT EXISTS(SELECT 1 FROM practices WHERE title = ? AND category_code = ?)"
                ),
                (
                    p["category_code"],
                    p["title"],
                    p.get("description"),
                    steps_json,
                    p.get("timer_seconds"),
                    p["title"],
                    p["category_code"],
                ),
            )
        # checklists
        for cl in SEED_JSON["checklists"]:
            await conn.execute(
                "INSERT OR IGNORE INTO checklists(code, title) VALUES(?, ?)",
                (cl["code"], cl["title"]),
            )
            for idx, item in enumerate(cl.get("items", [])):
                await conn.execute(
                    (
                        "INSERT INTO checklist_items(checklist_code, title, order_index)\n"
                        "SELECT ?, ?, ?\n"
                        "WHERE NOT EXISTS(SELECT 1 FROM checklist_items WHERE checklist_code = ? AND title = ?)"
                    ),
                    (cl["code"], item, idx, cl["code"], item),
                )
        await conn.commit()

    # User helpers
    async def upsert_user(self, user_id: int, first_name: Optional[str], username: Optional[str]) -> None:
        conn = await self.connect()
        await conn.execute(
            (
                "INSERT INTO users(user_id, first_name, username) VALUES(?, ?, ?)\n"
                "ON CONFLICT(user_id) DO UPDATE SET first_name=excluded.first_name, username=excluded.username"
            ),
            (user_id, first_name, username),
        )
        await conn.commit()

    async def list_categories(self) -> List[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute("SELECT code, title FROM categories ORDER BY title") as cur:
            return await cur.fetchall()

    async def list_practices_by_category(self, category_code: str) -> List[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute(
            "SELECT id, title FROM practices WHERE is_active=1 AND category_code=? ORDER BY id DESC",
            (category_code,),
        ) as cur:
            return await cur.fetchall()

    async def get_practice(self, practice_id: int) -> Optional[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute(
            "SELECT id, title, description, steps_json, timer_seconds FROM practices WHERE id=?",
            (practice_id,),
        ) as cur:
            row = await cur.fetchone()
            return row

    async def random_practice(self) -> Optional[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute(
            "SELECT id, title, description, steps_json, timer_seconds FROM practices WHERE is_active=1 ORDER BY RANDOM() LIMIT 1"
        ) as cur:
            return await cur.fetchone()

    async def add_journal_entry(self, user_id: int, state: str, note: Optional[str]) -> None:
        conn = await self.connect()
        await conn.execute(
            "INSERT INTO journal_entries(user_id, state, note) VALUES(?, ?, ?)",
            (user_id, state, note),
        )
        await conn.commit()

    async def list_checklists(self) -> List[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute("SELECT code, title FROM checklists ORDER BY title") as cur:
            return await cur.fetchall()

    async def list_checklist_items(self, checklist_code: str) -> List[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute(
            (
                "SELECT ci.id, ci.title, IFNULL(ucp.done, 0) as done FROM checklist_items ci\n"
                "LEFT JOIN user_checklist_progress ucp ON ucp.checklist_item_id = ci.id\n"
                "     AND ucp.user_id = ?\n"
                "WHERE ci.checklist_code = ? ORDER BY ci.order_index ASC, ci.id ASC"
            ),
            (0, checklist_code),
        ) as cur:
            return await cur.fetchall()

    async def toggle_checklist_item(self, user_id: int, item_id: int) -> None:
        conn = await self.connect()
        # read current
        async with conn.execute(
            "SELECT done FROM user_checklist_progress WHERE user_id=? AND checklist_item_id=?",
            (user_id, item_id),
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            await conn.execute(
                "INSERT INTO user_checklist_progress(user_id, checklist_item_id, done) VALUES(?, ?, 1)",
                (user_id, item_id),
            )
        else:
            new_done = 0 if int(row["done"]) else 1
            await conn.execute(
                "UPDATE user_checklist_progress SET done=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND checklist_item_id=?",
                (new_done, user_id, item_id),
            )
        await conn.commit()

    async def add_points(self, user_id: int, points: int) -> None:
        conn = await self.connect()
        await conn.execute(
            "INSERT INTO users(user_id, points) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points + excluded.points",
            (user_id, points),
        )
        await conn.commit()

    async def set_last_daily_sent(self, user_id: int, date_str: str) -> None:
        conn = await self.connect()
        await conn.execute(
            "UPDATE users SET last_daily_sent=? WHERE user_id=?",
            (date_str, user_id),
        )
        await conn.commit()

    async def list_users_for_daily(self) -> List[int]:
        conn = await self.connect()
        async with conn.execute(
            "SELECT user_id FROM users WHERE IFNULL(daily_enabled,1)=1"
        ) as cur:
            rows = await cur.fetchall()
            return [int(r["user_id"]) for r in rows]

    # Gamification helpers
    async def log_practice_completion(self, user_id: int, practice_id: int) -> None:
        conn = await self.connect()
        await conn.execute(
            "INSERT INTO user_practice_log(user_id, practice_id) VALUES(?, ?)",
            (user_id, practice_id),
        )
        await conn.commit()

    async def get_user_points(self, user_id: int) -> int:
        conn = await self.connect()
        async with conn.execute(
            "SELECT IFNULL(points,0) as p FROM users WHERE user_id=?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return int(row["p"]) if row else 0

    async def grant_achievement(self, user_id: int, code: str) -> bool:
        conn = await self.connect()
        try:
            await conn.execute(
                "INSERT INTO user_achievements(user_id, achievement_code) VALUES(?, ?)",
                (user_id, code),
            )
            await conn.commit()
            return True
        except Exception:
            return False

    async def list_user_achievements(self, user_id: int) -> List[aiosqlite.Row]:
        conn = await self.connect()
        async with conn.execute(
            (
                "SELECT ua.achievement_code as code, a.title as title FROM user_achievements ua\n"
                "JOIN achievements a ON a.code = ua.achievement_code WHERE ua.user_id=? ORDER BY ua.earned_at DESC"
            ),
            (user_id,),
        ) as cur:
            return await cur.fetchall()

    async def count_journal_entries(self, user_id: int) -> int:
        conn = await self.connect()
        async with conn.execute(
            "SELECT COUNT(*) as c FROM journal_entries WHERE user_id=?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return int(row["c"]) if row else 0

    async def count_practice_completions(self, user_id: int) -> int:
        conn = await self.connect()
        async with conn.execute(
            "SELECT COUNT(*) as c FROM user_practice_log WHERE user_id=?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return int(row["c"]) if row else 0

    async def get_practice_streak_days(self, user_id: int) -> int:
        # Calculate consecutive day streak including today if any entry exists today
        conn = await self.connect()
        async with conn.execute(
            (
                "SELECT DATE(performed_at) as d FROM user_practice_log WHERE user_id=?\n"
                "AND performed_at >= DATE('now','-21 day') GROUP BY DATE(performed_at) ORDER BY d DESC"
            ),
            (user_id,),
        ) as cur:
            rows = await cur.fetchall()
        dates = [row["d"] for row in rows]
        if not dates:
            return 0
        from datetime import date, timedelta

        today = date.today()
        streak = 0
        current = today
        date_set = set(dates)
        while current.isoformat() in date_set:
            streak += 1
            current = current - timedelta(days=1)
        return streak


