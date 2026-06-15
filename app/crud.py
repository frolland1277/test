"""Generic, table-agnostic CRUD helpers built on top of sqlite3.

Every endpoint resolves to one of these three operations. The table name is
never taken from user input — callers pass a hard-coded, validated table name
from the route definitions, so string interpolation here is safe.
"""
import sqlite3
from typing import Any, Optional

from fastapi import HTTPException

from .db import get_connection


def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    """Insert a row and return the created record."""
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    conn = get_connection()
    try:
        cur = conn.execute(sql, list(data.values()))
        conn.commit()
        return select_one(table, cur.lastrowid, conn=conn)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()


def select_all(table: str) -> list[dict[str, Any]]:
    """Return all rows from a table."""
    conn = get_connection()
    try:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def select_one(
    table: str, row_id: int, conn: Optional[sqlite3.Connection] = None
) -> dict[str, Any]:
    """Return a single row by id, or raise 404."""
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE id = ?", (row_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"{table} {row_id} not found")
        return dict(row)
    finally:
        if own_conn:
            conn.close()


def delete(table: str, row_id: int) -> None:
    """Delete a row by id, or raise 404 if it does not exist."""
    conn = get_connection()
    try:
        cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"{table} {row_id} not found")
    finally:
        conn.close()
