"""SQLite wrapper for the response store.

Single table; one row per respondent. Answers to multi-select questions are
stored as JSON strings.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from core.config import DB_PATH
from core.grouper import Participant


_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS responses (
    respondent_id TEXT PRIMARY KEY,
    submitted_at  TEXT NOT NULL,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    role          TEXT,
    years_exp     TEXT,
    q5            INTEGER,
    q6            INTEGER,
    q7            TEXT,
    q8            TEXT,
    q9            TEXT,
    q10           TEXT,
    q11           TEXT,
    q12           TEXT,
    q13           TEXT,
    q14           TEXT,
    q15           TEXT,
    q16           TEXT,
    score         INTEGER NOT NULL,
    level         TEXT NOT NULL,
    breakdown     TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def email_exists(email: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM responses WHERE email = ? COLLATE NOCASE LIMIT 1",
            (email.strip(),),
        ).fetchone()
    return row is not None


def respondent_exists(respondent_id: str) -> bool:
    if not respondent_id:
        return False
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM responses WHERE respondent_id = ? LIMIT 1",
            (respondent_id,),
        ).fetchone()
    return row is not None


def get_respondent_name(respondent_id: str) -> str | None:
    if not respondent_id:
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT name FROM responses WHERE respondent_id = ? LIMIT 1",
            (respondent_id,),
        ).fetchone()
    return row["name"] if row else None


def insert_submission(
    *,
    name: str,
    email: str,
    role: str,
    years_exp: str,
    answers: dict[str, Any],
    score: int,
    level: str,
    breakdown: dict[str, int],
) -> str:
    """Insert a new submission. Returns the generated respondent_id."""
    respondent_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO responses (
                respondent_id, submitted_at,
                name, email, role, years_exp,
                q5, q6, q7, q8, q9, q10,
                q11, q12, q13, q14, q15, q16,
                score, level, breakdown
            ) VALUES (
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?
            )
            """,
            (
                respondent_id, now,
                name.strip(), email.strip(), role, years_exp,
                answers.get("q5"),
                answers.get("q6"),
                json.dumps(answers.get("q7") or []),
                answers.get("q8"),
                answers.get("q9"),
                json.dumps(answers.get("q10") or []),
                answers.get("q11"),
                answers.get("q12"),
                answers.get("q13"),
                answers.get("q14"),
                answers.get("q15"),
                answers.get("q16"),
                score, level, json.dumps(breakdown),
            ),
        )
    return respondent_id


def delete_submission(respondent_id: str) -> bool:
    """Delete a submission by respondent_id. Returns True if a row was deleted."""
    if not respondent_id:
        return False
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM responses WHERE respondent_id = ?",
            (respondent_id,),
        )
        return cur.rowcount > 0


def fetch_all_for_dashboard() -> list[dict[str, Any]]:
    """Return every submission as a dict, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM responses ORDER BY submitted_at DESC"
        ).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        d = dict(r)
        d["q7"] = json.loads(d["q7"] or "[]")
        d["q10"] = json.loads(d["q10"] or "[]")
        d["breakdown"] = json.loads(d["breakdown"] or "{}")
        out.append(d)
    return out


def fetch_participants() -> list[Participant]:
    """Return lightweight Participant records for the grouper."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT respondent_id, name, email, role, score, level "
            "FROM responses ORDER BY submitted_at ASC"
        ).fetchall()
    return [
        Participant(
            respondent_id=r["respondent_id"],
            name=r["name"],
            email=r["email"],
            role=r["role"] or "",
            score=r["score"],
            level=r["level"],
        )
        for r in rows
    ]


def get_setting(key: str, default: str = "") -> str:
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


def count_submissions() -> int:
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM responses").fetchone()
    return row["n"] if row else 0
