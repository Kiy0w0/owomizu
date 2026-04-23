import asyncio
import threading
from queue import Queue

import aiosqlite


class DatabaseWorker:
    def __init__(self, db_path="utils/data/db.sqlite"):
        self.db_path = db_path
        self._queue = Queue()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._worker())

    def write(self, sql: str, params=None):
        self._queue.put((sql, params))

    async def read(self, sql: str, params=None):
        async with aiosqlite.connect(self.db_path, timeout=5) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, params or ()) as cursor:
                return await cursor.fetchall()

    async def _worker(self):
        import os
        os.makedirs("utils/data", exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.commit()

            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_data (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.commit()

            while True:
                sql, params = await self._loop.run_in_executor(None, self._queue.get)
                try:
                    await db.execute(sql, params or ())
                    await db.commit()
                except Exception as e:
                    print(f"[DB] Error: {e}")
                finally:
                    self._queue.task_done()
                    await asyncio.sleep(0.05)

    async def get_value(self, key: str):
        rows = await self.read(
            "SELECT value FROM bot_data WHERE key = ?", (key,)
        )
        return rows[0]["value"] if rows else None

    def set_value(self, key: str, value: str):
        self.write(
            "INSERT OR REPLACE INTO bot_data (key, value) VALUES (?, ?)",
            (key, str(value)),
        )


db = DatabaseWorker()
