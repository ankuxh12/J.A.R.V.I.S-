
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jarvis_memory.db"


def connect():
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)


def save_memory(key, value):
    initialize_memory()

    with connect() as conn:
        conn.execute("""
            INSERT INTO memories (key, value)
            VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
        """, (key.lower().strip(), value.strip()))


def get_memory(key):
    initialize_memory()

    with connect() as conn:
        result = conn.execute(
            "SELECT value FROM memories WHERE key = ?",
            (key.lower().strip(),)
        ).fetchone()

    return result[0] if result else None


def get_all_memories():
    initialize_memory()

    with connect() as conn:
        rows = conn.execute(
            "SELECT key, value FROM memories ORDER BY key"
        ).fetchall()

    return dict(rows)


def delete_memory(key):
    initialize_memory()

    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM memories WHERE key = ?",
            (key.lower().strip(),)
        )
        return cursor.rowcount > 0


def clear_all_memories():
    initialize_memory()

    with connect() as conn:
        conn.execute("DELETE FROM memories")


if __name__ == "__main__":
    save_memory("favorite superhero", "Iron Man")
    print(get_memory("favorite superhero"))
    print(get_all_memories())
