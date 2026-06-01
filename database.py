import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "tasks.db")


def init_database():
    conn = sqlite3.connect("DB_PATH")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        list_name TEXT NOT NULL,
        text TEXT NOT NULL,
        task_time TEXT,
        repeat_time TEXT,
        done INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT,
        solve_date TEXT,
        special INTEGER DEFAULT 0,
        comment TEXT
    )
    """)
    conn.commit()
    conn.close()


# DATABASE ACCESS
def execute(query, params=()):
    conn = sqlite3.connect("DB_PATH")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def fetchall(query, params=()):
    conn = sqlite3.connect("DB_PATH")
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result


def fetchone(query, params=()):
    conn = sqlite3.connect("DB_PATH")
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result
