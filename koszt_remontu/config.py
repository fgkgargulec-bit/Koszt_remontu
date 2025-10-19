"""Proste przechowywanie konfiguracji dla aplikacji i CLI."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path.home() / ".koszt_remontu_settings.json"

_DEFAULT_CONFIG: Dict[str, Any] = {
    "base": "",
    "travel_rate": 0.0,
    "services": [],
}


def load_config() -> Dict[str, Any]:
    """Wczytaj konfigurację z dysku."""

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            return dict(_DEFAULT_CONFIG)
        merged = dict(_DEFAULT_CONFIG)
        merged.update({k: v for k, v in data.items() if k in _DEFAULT_CONFIG})
        services = merged.get("services", [])
        if not isinstance(services, list):
            services = []
        merged["services"] = services
        return merged
    return dict(_DEFAULT_CONFIG)


def save_config(config: Dict[str, Any]) -> None:
    """Zapisz konfigurację na dysku."""

    merged = dict(_DEFAULT_CONFIG)
    for key in _DEFAULT_CONFIG:
        value = config.get(key, _DEFAULT_CONFIG[key])
        if key == "services":
            if not isinstance(value, list):
                value = []
            else:
                sanitized = []
                for service in value:
                    if not isinstance(service, dict):
                        continue
                    name = str(service.get("name", "")).strip()
                    if not name:
                        continue
                    unit = str(service.get("unit", "")).strip()
                    if not unit:
                        continue
                    try:
                        rate = float(service.get("rate", 0.0))
                    except (TypeError, ValueError):
                        continue
                    sanitized.append({"name": name, "unit": unit, "rate": rate})
                value = sanitized
        merged[key] = value
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), "utf-8")


def update_config(**kwargs: Any) -> Dict[str, Any]:
    """Zaktualizuj i zwróć konfigurację."""

    config = load_config()
    config.update({k: v for k, v in kwargs.items() if k in _DEFAULT_CONFIG})
    save_config(config)
    return config


def add_or_update_service(name: str, unit: str, rate: float) -> Dict[str, Any]:
    """Dodaj lub zaktualizuj usługę i zwróć aktualną konfigurację."""

    config = load_config()
    services = config.get("services", [])
    name_key = name.casefold()
    services = [
        service
        for service in services
        if str(service.get("name", "")).casefold() != name_key
    ]
    services.append({"name": name, "unit": unit, "rate": rate})
    config["services"] = services
    save_config(config)
    return config


def list_services() -> list[Dict[str, Any]]:
    """Zwróć listę zapisanych usług."""

    config = load_config()
    services = config.get("services", [])
    if not isinstance(services, list):
        return []
    return services
