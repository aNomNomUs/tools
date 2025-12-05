"""Command-line interface for the offline AstroTalk clone."""

from __future__ import annotations

import argparse
import json
from datetime import date
from typing import Any, Callable, Dict

from .compatibility import compatibility_report
from .horoscope import HoroscopeEngine
from .profile import profile_payload
from .utils import sanitize_sign_name


def _date_type(raw: str) -> date:
    try:
        parts = [int(part) for part in raw.split("-")]
        if len(parts) != 3:
            raise ValueError
        return date(parts[0], parts[1], parts[2])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must be in YYYY-MM-DD format.") from exc


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline astrology toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    horoscope_parser = sub.add_parser("horoscope", help="Generate a horoscope for a sign and date.")
    horoscope_parser.add_argument("sign", help="Zodiac sign name.")
    horoscope_parser.add_argument("date", type=_date_type, help="Target date in YYYY-MM-DD format.")

    compat_parser = sub.add_parser("compatibility", help="Compatibility report for two signs.")
    compat_parser.add_argument("primary", help="Primary sign name.")
    compat_parser.add_argument("partner", help="Partner sign name.")

    profile_parser = sub.add_parser("profile", help="Resolve sign from a birthday and name.")
    profile_parser.add_argument("name", help="User name for the profile payload.")
    profile_parser.add_argument("birthday", type=_date_type, help="Birthday in YYYY-MM-DD format.")

    args = parser.parse_args(argv)

    actions: Dict[str, Callable[[], Dict[str, Any] | str]] = {
        "horoscope": lambda: _handle_horoscope(args.sign, args.date),
        "compatibility": lambda: compatibility_report(
            sanitize_sign_name(args.primary), sanitize_sign_name(args.partner)
        ),
        "profile": lambda: profile_payload(args.name, args.birthday),
    }

    payload = actions[args.command]()
    if isinstance(payload, str):
        print(payload)
    else:
        print(json.dumps(payload, indent=2))
    return 0


def _handle_horoscope(sign: str, target_date: date) -> str:
    normalized = sanitize_sign_name(sign)
    engine = HoroscopeEngine()
    return engine.generate(normalized, target_date)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
