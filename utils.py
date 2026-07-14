"""Small validation and formatting helpers."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value: str) -> bool:
    return not value or bool(EMAIL_RE.match(value.strip()))


def is_valid_url(value: str) -> bool:
    if not value:
        return True
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def iso_date(value: date | None) -> str:
    return value.isoformat() if value else ""


def safe_int(value, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
