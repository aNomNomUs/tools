"""Deterministic horoscope generation without network dependencies."""

from __future__ import annotations

from datetime import date
from typing import Dict

from .constants import HOROSCOPE_TEMPLATES, ZODIAC_SIGNS
from .utils import derive_seed, pick_deterministic


class HoroscopeEngine:
    """Generates reproducible horoscopes for a given sign and date."""

    def __init__(self, templates=HOROSCOPE_TEMPLATES):
        if not templates:
            raise ValueError("At least one template is required to generate horoscopes.")
        self.templates = templates

    def generate(self, sign: str, target_date: date) -> str:
        """Return a horoscope for ``sign`` on ``target_date``.

        Input is validated strictly to avoid unexpected behavior. Horoscopes are
        deterministic for the same sign and date to support offline caching and
        predictable user experiences during testing.
        """

        if sign not in ZODIAC_SIGNS:
            raise ValueError(f"Unknown sign: {sign}")
        if not isinstance(target_date, date):
            raise TypeError("target_date must be a datetime.date instance")

        seed = derive_seed(sign, target_date.isoformat())
        template = pick_deterministic(self.templates, seed)
        trait = pick_deterministic(ZODIAC_SIGNS[sign].traits, seed)
        return template.format(trait=trait)

    def summary(self, sign: str) -> Dict[str, str]:
        """Return a short summary of sign traits for UI display."""

        if sign not in ZODIAC_SIGNS:
            raise ValueError(f"Unknown sign: {sign}")
        traits = ", ".join(ZODIAC_SIGNS[sign].traits)
        return {"sign": sign, "traits": traits}
