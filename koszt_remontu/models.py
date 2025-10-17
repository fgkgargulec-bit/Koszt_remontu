"""Definicje modeli domenowych."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PricingUnit(str, Enum):
    """Jednostka rozliczeniowa usługi."""

    SQUARE_METER = "sqm"
    HOUR = "hour"
    ITEM = "item"

    def human_readable(self) -> str:
        mapping = {
            PricingUnit.SQUARE_METER: "m²",
            PricingUnit.HOUR: "godzina",
            PricingUnit.ITEM: "pozycja",
        }
        return mapping[self]


@dataclass(slots=True)
class Service:
    """Usługa oferowana przez wykonawcę."""

    name: str
    unit: PricingUnit
    rate: float


@dataclass(slots=True)
class Settings:
    """Konfiguracja wykonawcy."""

    base_address: Optional[str] = None
    travel_rate_per_km: Optional[float] = None
