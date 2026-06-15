"""SQLite connection helpers and schema initialisation."""
import os
import sqlite3
from pathlib import Path

# Database file lives next to the repo root by default; override with DATABASE_PATH.
DB_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "app.db"))
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Open a connection with foreign keys enabled and row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the tables from schema.sql if they do not already exist."""
    schema = SCHEMA_PATH.read_text()
    conn = get_connection()
    try:
        # schema.sql uses plain CREATE TABLE; only run it on a fresh database.
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not existing:
            conn.executescript(schema)
            conn.commit()
    finally:
        conn.close()
