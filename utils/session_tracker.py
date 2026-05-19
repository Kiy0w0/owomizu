import sqlite3
import time
from datetime import datetime

_DB_PATH = "utils/data/session_history.db"


def init_db(db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            hunts INTEGER DEFAULT 0,
            battles INTEGER DEFAULT 0,
            commands INTEGER DEFAULT 0,
            captchas INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cash_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT NOT NULL,
            amount INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def start_session(db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    c.execute("UPDATE sessions SET end_time = ? WHERE end_time IS NULL", (time_str,))
    c.execute("INSERT INTO sessions (date, start_time) VALUES (?, ?)", (date_str, time_str))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_session(db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    time_str = datetime.now().strftime("%H:%M:%S")
    c.execute("UPDATE sessions SET end_time = ? WHERE end_time IS NULL", (time_str,))
    conn.commit()
    conn.close()


def _active_session_id(c):
    c.execute("SELECT id FROM sessions WHERE end_time IS NULL ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row:
        return row[0]
    now = datetime.now()
    c.execute(
        "INSERT INTO sessions (date, start_time) VALUES (?, ?)",
        (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")),
    )
    return c.lastrowid


def track_command(cmd_type: str, db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    sid = _active_session_id(c)
    c.execute("UPDATE sessions SET commands = commands + 1 WHERE id = ?", (sid,))
    if cmd_type == "hunt":
        c.execute("UPDATE sessions SET hunts = hunts + 1 WHERE id = ?", (sid,))
    elif cmd_type == "battle":
        c.execute("UPDATE sessions SET battles = battles + 1 WHERE id = ?", (sid,))
    elif cmd_type == "captcha":
        c.execute("UPDATE sessions SET captchas = captchas + 1 WHERE id = ?", (sid,))
    conn.commit()
    conn.close()


def track_cash(amount: int, db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    sid = _active_session_id(c)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO cash_snapshots (session_id, timestamp, amount) VALUES (?, ?, ?)",
        (sid, ts, amount),
    )
    c.execute("SELECT COUNT(*) FROM cash_snapshots WHERE session_id = ?", (sid,))
    if c.fetchone()[0] > 50:
        c.execute("""
            DELETE FROM cash_snapshots WHERE id NOT IN (
                SELECT id FROM cash_snapshots WHERE session_id = ?
                ORDER BY id DESC LIMIT 50
            ) AND session_id = ?
        """, (sid, sid))
    conn.commit()
    conn.close()


def get_session_stats(db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    c = conn.cursor()
    c.execute(
        "SELECT hunts, battles, commands, captchas FROM sessions "
        "WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {"hunts": row[0], "battles": row[1], "commands": row[2], "captchas": row[3]}
    return {"hunts": 0, "battles": 0, "commands": 0, "captchas": 0}


def get_all_time_stats(db_path=None):
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    c = conn.cursor()
    c.execute(
        "SELECT SUM(hunts), SUM(battles), SUM(commands), SUM(captchas), COUNT(id) FROM sessions"
    )
    row = c.fetchone()
    conn.close()
    if row and row[4]:
        return {
            "total_hunts": row[0] or 0,
            "total_battles": row[1] or 0,
            "total_commands": row[2] or 0,
            "total_captchas": row[3] or 0,
            "total_sessions": row[4],
        }
    return {"total_hunts": 0, "total_battles": 0, "total_commands": 0, "total_captchas": 0, "total_sessions": 0}
