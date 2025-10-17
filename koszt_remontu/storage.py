"""Warstwa przechowywania danych."""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from .models import PricingUnit, Service, Settings


class JsonStorage:
    """Przechowuje konfigurację w pliku JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(os.path.expanduser("~/.koszt_remontu/data.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"services": [], "settings": {}})

    # region Operacje wewnętrzne
    def _read(self) -> dict:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, data: dict) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    # endregion

    def list_services(self) -> List[Service]:
        data = self._read()
        services = []
        for raw in data.get("services", []):
            services.append(
                Service(
                    name=raw["name"],
                    unit=PricingUnit(raw["unit"]),
                    rate=float(raw["rate"]),
                )
            )
        return services

    def add_service(self, service: Service) -> None:
        data = self._read()
        services = data.setdefault("services", [])
        for existing in services:
            if existing["name"].lower() == service.name.lower():
                raise ValueError(f"Usługa '{service.name}' już istnieje")
        services.append(
            {
                "name": service.name,
                "unit": service.unit.value,
                "rate": service.rate,
            }
        )
        self._write(data)

    def remove_service(self, name: str) -> bool:
        data = self._read()
        services = data.get("services", [])
        filtered = [srv for srv in services if srv["name"].lower() != name.lower()]
        removed = len(services) != len(filtered)
        if removed:
            data["services"] = filtered
            self._write(data)
        return removed

    def get_settings(self) -> Settings:
        data = self._read()
        settings_data = data.get("settings", {})
        return Settings(
            base_address=settings_data.get("base_address"),
            travel_rate_per_km=settings_data.get("travel_rate_per_km"),
        )

    def update_settings(self, settings: Settings) -> None:
        data = self._read()
        data["settings"] = {k: v for k, v in asdict(settings).items() if v is not None}
        self._write(data)

    def iter_services(self) -> Iterable[Service]:
        yield from self.list_services()
