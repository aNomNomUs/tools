"""Static data for offline astrology logic.

This module defines zodiac sign metadata and internal templates used across
horoscope generation, compatibility scoring, and profile utilities. All data is
self-contained to avoid external lookups that would widen the attack surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ZodiacSign:
    """Represents a zodiac sign with a date range and traits."""

    name: str
    start: Tuple[int, int]
    end: Tuple[int, int]
    traits: Tuple[str, ...]

    def matches(self, target: date) -> bool:
        """Return True if ``target`` falls within this sign's date range.

        The ranges are expressed as (month, day) tuples. Capricorn spans the
        year boundary, so we treat that as a special case in the matcher.
        """

        month_day = (target.month, target.day)
        if self.name == "Capricorn":
            return month_day >= self.start or month_day <= self.end
        return self.start <= month_day <= self.end


ZODIAC_SIGNS: Dict[str, ZodiacSign] = {
    "Aries": ZodiacSign("Aries", (3, 21), (4, 19), ("courageous", "assertive", "direct")),
    "Taurus": ZodiacSign("Taurus", (4, 20), (5, 20), ("steady", "patient", "practical")),
    "Gemini": ZodiacSign("Gemini", (5, 21), (6, 20), ("curious", "adaptable", "communicative")),
    "Cancer": ZodiacSign("Cancer", (6, 21), (7, 22), ("nurturing", "protective", "intuitive")),
    "Leo": ZodiacSign("Leo", (7, 23), (8, 22), ("confident", "generous", "radiant")),
    "Virgo": ZodiacSign("Virgo", (8, 23), (9, 22), ("meticulous", "helpful", "grounded")),
    "Libra": ZodiacSign("Libra", (9, 23), (10, 22), ("harmonizing", "diplomatic", "balanced")),
    "Scorpio": ZodiacSign("Scorpio", (10, 23), (11, 21), ("intense", "resourceful", "perceptive")),
    "Sagittarius": ZodiacSign("Sagittarius", (11, 22), (12, 21), ("optimistic", "honest", "exploratory")),
    "Capricorn": ZodiacSign("Capricorn", (12, 22), (1, 19), ("disciplined", "ambitious", "strategic")),
    "Aquarius": ZodiacSign("Aquarius", (1, 20), (2, 18), ("inventive", "independent", "humanitarian")),
    "Pisces": ZodiacSign("Pisces", (2, 19), (3, 20), ("empathetic", "imaginative", "gentle")),
}

ZODIAC_ORDER: List[str] = list(ZODIAC_SIGNS.keys())

# Basic compatibility factors tuned to keep everything deterministic and local.
COMPATIBILITY_MATRIX: Dict[str, Dict[str, int]] = {}

for primary in ZODIAC_ORDER:
    COMPATIBILITY_MATRIX[primary] = {}
    for partner in ZODIAC_ORDER:
        # Deterministic but non-trivial scoring based on index distance.
        offset = abs(ZODIAC_ORDER.index(primary) - ZODIAC_ORDER.index(partner))
        score = max(30, 100 - offset * 5)
        # Shared traits bump synergy.
        shared = len(set(ZODIAC_SIGNS[primary].traits).intersection(ZODIAC_SIGNS[partner].traits))
        score = min(100, score + shared * 3)
        COMPATIBILITY_MATRIX[primary][partner] = score

HOROSCOPE_TEMPLATES: Tuple[str, ...] = (
    "Your {trait} energy attracts practical wins today. Anchor decisions in facts and let the rest roll off.",
    "Lean into your {trait} side, but keep boundaries so nobody freeloads on your sparkle.",
    "A surprising conversation may test your {trait} streak. Listen first, then pounce with clarity.",
    "Routine feels safer than risk, yet a calculated move could honor your {trait} nature without chaos.",
    "Your calendar is a circus, but your {trait} mindset keeps the spotlight where it belongs: on results.",
    "Give your nervous system a break—defend your {trait} values by scheduling actual downtime.",
)
