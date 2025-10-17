"""Moduł odpowiedzialny za kalkulację wycen."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from .models import Service


class Geocoder(Protocol):
    """Prosty protokół dla geokoderów."""

    def __call__(self, address: str) -> tuple[float, float]:
        """Zwraca krotkę (lat, lon)."""


@dataclass(slots=True)
class QuoteResult:
    """Szczegóły wyceny."""

    service_cost: float
    travel_distance_km: float
    travel_cost: float
    total_cost: float


class QuoteCalculator:
    """Kalkulator wyceny usługi."""

    def __init__(
        self,
        service_provider: Callable[[str], Optional[Service]],
        geocoder: Geocoder,
        base_address: str,
        travel_rate_per_km: float,
    ) -> None:
        self._service_provider = service_provider
        self._geocoder = geocoder
        self._base_address = base_address
        self._travel_rate_per_km = travel_rate_per_km

    def calculate(self, service_name: str, quantity: float, client_address: str) -> QuoteResult:
        if quantity <= 0:
            raise ValueError("Ilość musi być dodatnia")

        service = self._service_provider(service_name)
        if service is None:
            raise ValueError(f"Nie znaleziono usługi '{service_name}'")

        service_cost = service.rate * quantity

        base_location = self._geocode(self._base_address)
        client_location = self._geocode(client_address)
        distance = self._distance_km(base_location, client_location)
        travel_cost = distance * self._travel_rate_per_km

        return QuoteResult(
            service_cost=round(service_cost, 2),
            travel_distance_km=round(distance, 2),
            travel_cost=round(travel_cost, 2),
            total_cost=round(service_cost + travel_cost, 2),
        )

    def _geocode(self, address: str) -> tuple[float, float]:
        address = address.strip()
        if "," in address and all(part.strip().replace(".", "", 1).replace("-", "", 1).isdigit() for part in address.split(",")):
            lat_str, lon_str = address.split(",", 1)
            return float(lat_str), float(lon_str)
        return self._geocoder(address)

    @staticmethod
    def _distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
        """Haversine distance between two points."""

        lat1, lon1 = map(math.radians, a)
        lat2, lon2 = map(math.radians, b)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        sin_dlat = math.sin(dlat / 2)
        sin_dlon = math.sin(dlon / 2)
        h = sin_dlat**2 + math.cos(lat1) * math.cos(lat2) * sin_dlon**2
        return 2 * 6371.0 * math.asin(math.sqrt(h))
