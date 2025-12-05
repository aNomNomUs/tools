"""Utility helpers for deterministic and safe operations.

All helpers are stdlib-only to avoid supply-chain surprises and to keep runtime
footprints predictable in offline environments.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import date
from typing import Iterable


def sanitize_sign_name(raw: str) -> str:
    """Normalize a user-provided sign name defensively.

    - Strips whitespace
    - Title-cases while preserving Unicode characters
    - Rejects suspicious payloads by allowing only alphabetic characters and
      spaces after normalization.
    """

    normalized = raw.strip().title()
    if not normalized.replace(" ", "").isalpha():
        raise ValueError("Sign names must be alphabetic after trimming.")
    return normalized


def derive_seed(*values: Iterable[str]) -> int:
    """Create a deterministic integer seed from arbitrary strings.

    This avoids reliance on global randomness while ensuring the output remains
    stable for the same inputs. A small, local-only pepper is baked in to make
    naive precomputation harder without introducing secrets.
    """

    pepper = "offline-astro-pepper"
    message = "::".join(str(value) for value in values)
    digest = hmac.new(pepper.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big")


def pick_deterministic(sequence: Iterable[str], seed: int) -> str:
    """Choose a stable element from ``sequence`` using ``seed``.

    ``seed`` should already be derived from stable inputs via :func:`derive_seed`.
    The function guards against empty sequences to avoid runtime surprises.
    """

    items = tuple(sequence)
    if not items:
        raise ValueError("Cannot select from an empty sequence.")
    return items[seed % len(items)]


def days_since_epoch(target: date) -> int:
    """Return the number of days between ``target`` and the UNIX epoch."""

    epoch = date(1970, 1, 1)
    return (target - epoch).days


def obfuscated_id(*values: Iterable[str]) -> str:
    """Generate a short, non-sensitive identifier from inputs.

    Intended for logging correlation without leaking raw user input.
    """

    seed = derive_seed(*values)
    return secrets.token_hex(4) + f"-{seed % 10_000:04d}"
