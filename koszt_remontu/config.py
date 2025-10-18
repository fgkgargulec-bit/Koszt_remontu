"""Proste przechowywanie konfiguracji dla aplikacji i CLI."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path.home() / ".koszt_remontu_settings.json"

_DEFAULT_CONFIG: Dict[str, Any] = {"base": "", "travel_rate": 0.0}


def load_config() -> Dict[str, Any]:
    """Wczytaj konfigurację z dysku."""

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            return dict(_DEFAULT_CONFIG)
        merged = dict(_DEFAULT_CONFIG)
        merged.update({k: v for k, v in data.items() if k in _DEFAULT_CONFIG})
        return merged
    return dict(_DEFAULT_CONFIG)


def save_config(config: Dict[str, Any]) -> None:
    """Zapisz konfigurację na dysku."""

    merged = dict(_DEFAULT_CONFIG)
    merged.update({k: v for k, v in config.items() if k in _DEFAULT_CONFIG})
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), "utf-8")


def update_config(**kwargs: Any) -> Dict[str, Any]:
    """Zaktualizuj i zwróć konfigurację."""

    config = load_config()
    config.update({k: v for k, v in kwargs.items() if k in _DEFAULT_CONFIG})
    save_config(config)
    return config
