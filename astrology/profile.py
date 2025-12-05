"""Profile helpers for determining signs and formatting payloads."""

from __future__ import annotations

from datetime import date
from typing import Dict

from .constants import ZODIAC_SIGNS


def sign_from_birthday(birthday: date) -> str:
    """Return a zodiac sign for the provided birthday."""

    if not isinstance(birthday, date):
        raise TypeError("birthday must be a datetime.date instance")
    for sign in ZODIAC_SIGNS.values():
        if sign.matches(birthday):
            return sign.name
    raise ValueError("Could not map birthday to a zodiac sign.")


def profile_payload(name: str, birthday: date) -> Dict[str, str]:
    """Return a safe, minimal profile representation."""

    sign = sign_from_birthday(birthday)
    safe_name = name.strip()
    if not safe_name:
        raise ValueError("Name must not be empty.")
    return {"name": safe_name, "sign": sign, "birthday": birthday.isoformat()}
