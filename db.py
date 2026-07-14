"""SQLite persistence layer for job applications."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pandas as pd

STATUSES = ["Saved", "Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]
PRIORITIES = ["Low", "Medium", "High"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT DEFAULT '',
    job_type TEXT DEFAULT 'Remote',
    source TEXT DEFAULT '',
    job_url TEXT DEFAULT '',
    salary_range TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Saved',
    applied_date TEXT DEFAULT '',
    deadline TEXT DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'Medium',
    contact_person TEXT DEFAULT '',
    contact_email TEXT DEFAULT '',
    cv_version TEXT DEFAULT '',
    match_score INTEGER,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company);
CREATE INDEX IF NOT EXISTS idx_applications_applied_date ON applications(applied_date);
"""

ALLOWED_FIELDS = {
    "company", "role", "location", "job_type", "source", "job_url", "salary_range",
    "status", "applied_date", "deadline", "priority", "contact_person", "contact_email",
    "cv_version", "match_score", "notes"
}


@contextmanager
def connect(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def add_application(db_path: str | Path, data: dict[str, Any]) -> int:
    clean = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    if not str(clean.get("company", "")).strip() or not str(clean.get("role", "")).strip():
        raise ValueError("Company and role are required.")
    if clean.get("status") and clean["status"] not in STATUSES:
        raise ValueError("Invalid status.")
    if clean.get("priority") and clean["priority"] not in PRIORITIES:
        raise ValueError("Invalid priority.")

    fields = list(clean)
    placeholders = ", ".join("?" for _ in fields)
    query = f"INSERT INTO applications ({', '.join(fields)}) VALUES ({placeholders})"
    with connect(db_path) as conn:
        cur = conn.execute(query, [clean[f] for f in fields])
        return int(cur.lastrowid)


def update_application(db_path: str | Path, application_id: int, updates: dict[str, Any]) -> None:
    clean = {k: v for k, v in updates.items() if k in ALLOWED_FIELDS}
    if not clean:
        return
    if clean.get("status") and clean["status"] not in STATUSES:
        raise ValueError("Invalid status.")
    if clean.get("priority") and clean["priority"] not in PRIORITIES:
        raise ValueError("Invalid priority.")

    assignments = ", ".join(f"{field} = ?" for field in clean)
    values = [clean[field] for field in clean]
    with connect(db_path) as conn:
        conn.execute(
            f"UPDATE applications SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [*values, application_id],
        )


def delete_application(db_path: str | Path, application_id: int) -> None:
    with connect(db_path) as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (application_id,))


def get_application(db_path: str | Path, application_id: int) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
        return dict(row) if row else None


def list_applications(
    db_path: str | Path,
    statuses: list[str] | None = None,
    search: str = "",
) -> pd.DataFrame:
    query = "SELECT * FROM applications WHERE 1=1"
    params: list[Any] = []
    if statuses:
        query += f" AND status IN ({', '.join('?' for _ in statuses)})"
        params.extend(statuses)
    if search.strip():
        query += " AND (LOWER(company) LIKE ? OR LOWER(role) LIKE ? OR LOWER(location) LIKE ?)"
        needle = f"%{search.lower().strip()}%"
        params.extend([needle, needle, needle])
    query += " ORDER BY COALESCE(NULLIF(applied_date, ''), created_at) DESC, id DESC"
    with connect(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params)


def clear_all(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.execute("DELETE FROM applications")


def seed_demo_data(db_path: str | Path) -> int:
    with connect(db_path) as conn:
        existing = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        if existing:
            return 0

    demo = [
        {
            "company": "Nordic Byte Labs", "role": "Junior Python Developer", "location": "Helsinki, Finland",
            "job_type": "Hybrid", "source": "LinkedIn", "status": "Applied", "applied_date": "2026-07-03",
            "priority": "High", "match_score": 78, "cv_version": "CV-Python-v2",
            "notes": "Follow up after seven days. Portfolio project included."
        },
        {
            "company": "Arctic Analytics", "role": "Data Analyst Intern", "location": "Remote / Finland",
            "job_type": "Remote", "source": "Company website", "status": "Interview", "applied_date": "2026-06-27",
            "priority": "High", "match_score": 72, "cv_version": "CV-Data-v1",
            "notes": "Prepare SQL, pandas, and business-case examples."
        },
        {
            "company": "Saimaa Software", "role": "WordPress Support Assistant", "location": "Lappeenranta, Finland",
            "job_type": "Part-time", "source": "Direct outreach", "status": "Screening", "applied_date": "2026-07-08",
            "priority": "Medium", "match_score": 84, "cv_version": "CV-Support-v3",
            "notes": "Mention WordPress, SEO, customer support, and availability."
        },
        {
            "company": "Cloudberry Tech", "role": "Machine Learning Trainee", "location": "Espoo, Finland",
            "job_type": "Hybrid", "source": "Job board", "status": "Saved", "deadline": "2026-07-30",
            "priority": "Medium", "match_score": 61, "cv_version": "CV-AI-v1",
            "notes": "Needs stronger PyTorch evidence before applying."
        },
        {
            "company": "Polar Commerce", "role": "Technical Support Intern", "location": "Remote",
            "job_type": "Remote", "source": "Referral", "status": "Rejected", "applied_date": "2026-06-15",
            "priority": "Low", "match_score": 69, "cv_version": "CV-Support-v2",
            "notes": "Rejected after screening. Improve concise spoken examples."
        },
    ]
    for item in demo:
        add_application(db_path, item)
    return len(demo)
