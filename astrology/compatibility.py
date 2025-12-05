"""Compatibility scoring and descriptive helpers."""

from __future__ import annotations

from typing import Dict

from .constants import COMPATIBILITY_MATRIX, ZODIAC_SIGNS


def compatibility_score(primary: str, partner: str) -> int:
    """Return a deterministic compatibility score between two signs."""

    if primary not in ZODIAC_SIGNS:
        raise ValueError(f"Unknown primary sign: {primary}")
    if partner not in ZODIAC_SIGNS:
        raise ValueError(f"Unknown partner sign: {partner}")
    return COMPATIBILITY_MATRIX[primary][partner]


def compatibility_report(primary: str, partner: str) -> Dict[str, str]:
    """Produce a short compatibility report for UX consumption."""

    score = compatibility_score(primary, partner)
    vibe = _score_to_vibe(score)
    return {
        "primary": primary,
        "partner": partner,
        "score": str(score),
        "vibe": vibe,
    }


def _score_to_vibe(score: int) -> str:
    if score >= 85:
        return "Cosmic cheat code—run with it."
    if score >= 70:
        return "Solid vibes with a dash of adult conversation."
    if score >= 55:
        return "Potential if you both use your words and calendars."
    if score >= 45:
        return "Treat like a beta release: monitor closely."
    return "Probably fine for memes, less so for life plans."
