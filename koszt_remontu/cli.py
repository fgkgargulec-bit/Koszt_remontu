"""Prosty interfejs wiersza poleceń dla aplikacji Koszt Remontu."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from .config import (
    CONFIG_PATH,
    add_or_update_service,
    list_services,
    load_config,
    update_config,
)


class CliError(Exception):
    """Błąd walidacji parametrów CLI."""


_UNIT_ALIASES = {
    "sqm": {
        "sqm",
        "m2",
        "m^2",
        "metr kwadratowy",
        "metry kwadratowe",
        "metry_kwadratowe",
    },
    "hour": {"hour", "h", "godzina", "godziny"},
    "item": {"item", "szt", "sztuka", "sztuki"},
}


def _normalize_unit(unit: str) -> str:
    normalized = unit.strip().lower()
    for canonical, aliases in _UNIT_ALIASES.items():
        if normalized in aliases:
            return canonical
    raise CliError(
        "Nieobsługiwana jednostka. Wybierz spośród: metry kwadratowe, godziny, sztuki"
    )


def _cmd_set_base(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.base:
        raise CliError("Adres bazy nie może być pusty")
    return update_config(base=args.base)


def _cmd_set_travel_rate(args: argparse.Namespace) -> Dict[str, Any]:
    try:
        rate = float(args.travel_rate)
    except ValueError as exc:
        raise CliError("Stawka za kilometr musi być liczbą") from exc
    if rate < 0:
        raise CliError("Stawka za kilometr nie może być ujemna")
    return update_config(travel_rate=rate)


def _parse_payload() -> Optional[Dict[str, Any]]:
    if sys.stdin.isatty():
        return None
    payload = sys.stdin.read().strip()
    if not payload:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise CliError("Dostarczone dane nie są poprawnym JSON-em") from exc


def _cmd_quote(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.service:
        raise CliError("Nazwa usługi jest wymagana")
    if args.quantity <= 0:
        raise CliError("Ilość musi być dodatnia")
    if not args.client_address:
        raise CliError("Adres klienta jest wymagany")

    payload = _parse_payload() or {}

    config = load_config()
    travel_rate = float(config.get("travel_rate", 0.0))
    distance_km = float(payload.get("distance_km", payload.get("distance", 0)) or 0)
    travel_cost = round(distance_km * travel_rate, 2)

    response: Dict[str, Any] = {
        "service": args.service,
        "quantity": args.quantity,
        "client_address": args.client_address,
        "base": config.get("base"),
        "travel_rate": travel_rate,
        "travel_distance_km": distance_km,
        "travel_cost": travel_cost,
        "details": payload or {},
    }
    return response


def _cmd_service_add(args: argparse.Namespace) -> Dict[str, Any]:
    name = args.name.strip()
    if not name:
        raise CliError("Nazwa usługi jest wymagana")
    try:
        rate = float(args.rate)
    except ValueError as exc:
        raise CliError("Stawka za usługę musi być liczbą") from exc
    if rate < 0:
        raise CliError("Stawka za usługę nie może być ujemna")
    unit = _normalize_unit(args.unit)
    config = add_or_update_service(name=name, unit=unit, rate=rate)
    return {"services": config.get("services", [])}


def _cmd_service_list(args: argparse.Namespace) -> Dict[str, Any]:
    return {"services": list_services()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    settings = subparsers.add_parser("settings", help="Operacje na konfiguracji")
    settings_sub = settings.add_subparsers(dest="settings_cmd", required=True)

    set_base = settings_sub.add_parser("set-base", help="Ustaw adres bazy")
    set_base.add_argument("base", help="Adres bazy serwisu")
    set_base.set_defaults(func=_cmd_set_base)

    set_rate = settings_sub.add_parser(
        "set-travel-rate", help="Ustaw stawkę za kilometr dojazdu"
    )
    set_rate.add_argument("travel_rate", help="Kwota w PLN")
    set_rate.set_defaults(func=_cmd_set_travel_rate)

    quote = subparsers.add_parser(
        "quote",
        help="Wycena usługi",
        aliases=["price"],
    )
    quote.add_argument("--service", required=True, help="Nazwa usługi")
    quote.add_argument("--quantity", required=True, type=int, help="Ilość")
    quote.add_argument(
        "--client-address", required=True, help="Adres realizacji usługi"
    )
    quote.set_defaults(func=_cmd_quote)

    service = subparsers.add_parser("service", help="Zarządzanie usługami")
    service_sub = service.add_subparsers(dest="service_cmd", required=True)

    service_add = service_sub.add_parser(
        "add", help="Dodaj lub zaktualizuj usługę w konfiguracji"
    )
    service_add.add_argument("name", help="Nazwa usługi")
    service_add.add_argument(
        "--unit",
        required=True,
        help="Jednostka rozliczeniowa (np. metry kwadratowe, godziny, sztuki)",
    )
    service_add.add_argument("--rate", required=True, help="Stawka za jednostkę w PLN")
    service_add.set_defaults(func=_cmd_service_add)

    service_list = service_sub.add_parser("list", help="Wyświetl zapisane usługi")
    service_list.set_defaults(func=_cmd_service_list)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        result = args.func(args)
    except CliError as exc:
        parser.exit(status=1, message=f"{exc}\n")
    except AttributeError:
        parser.print_help()
        return 1

    if result is not None:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
