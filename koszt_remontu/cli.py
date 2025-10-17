"""Interfejs wiersza poleceń aplikacji."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .costs import QuoteCalculator
from .models import PricingUnit, Service
from .storage import JsonStorage


def geocode(address: str, *, user_agent: str = "koszt-remontu-cli") -> tuple[float, float]:
    """Geokodowanie adresu za pomocą API Nominatim."""

    url = "https://nominatim.openstreetmap.org/search"
    params = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
    request = urllib.request.Request(f"{url}?{params}")
    request.add_header("User-Agent", user_agent)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.URLError as exc:  # pragma: no cover - zależy od sieci
        raise ValueError(f"Błąd geokodowania: {exc}") from exc
    data = json.loads(payload)
    if not data:
        raise ValueError(f"Nie można znaleźć adresu: {address}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kalkulator kosztów remontu")
    parser.add_argument(
        "--storage",
        type=Path,
        default=None,
        help="Ścieżka do pliku z danymi (domyślnie ~/.koszt_remontu/data.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    service_parser = subparsers.add_parser("service", help="Zarządzanie usługami")
    service_sub = service_parser.add_subparsers(dest="service_command", required=True)

    service_add = service_sub.add_parser("add", help="Dodaje usługę")
    service_add.add_argument("name", help="Nazwa usługi")
    service_add.add_argument(
        "--unit",
        choices=[unit.value for unit in PricingUnit],
        default=PricingUnit.SQUARE_METER.value,
        help="Jednostka rozliczeniowa",
    )
    service_add.add_argument("--rate", type=float, required=True, help="Stawka za jednostkę")

    service_list = service_sub.add_parser("list", help="Wyświetla usługi")

    service_remove = service_sub.add_parser("remove", help="Usuwa usługę")
    service_remove.add_argument("name", help="Nazwa usługi do usunięcia")

    settings_parser = subparsers.add_parser("settings", help="Konfiguracja wykonawcy")
    settings_sub = settings_parser.add_subparsers(dest="settings_command", required=True)

    settings_show = settings_sub.add_parser("show", help="Wyświetla ustawienia")

    settings_base = settings_sub.add_parser("set-base", help="Ustawia adres bazowy")
    settings_base.add_argument("address", help="Adres bazowy")

    settings_rate = settings_sub.add_parser("set-travel-rate", help="Ustawia stawkę za kilometr")
    settings_rate.add_argument("rate", type=float, help="Stawka za kilometr")

    quote_parser = subparsers.add_parser("quote", help="Oblicza wycenę")
    quote_parser.add_argument("--service", required=True, help="Nazwa usługi")
    quote_parser.add_argument("--quantity", type=float, required=True, help="Ilość jednostek")
    quote_parser.add_argument("--client-address", required=True, help="Adres klienta")

    return parser


def handle_args(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    storage = JsonStorage(args.storage)

    if args.command == "service":
        if args.service_command == "add":
            service = Service(
                name=args.name,
                unit=PricingUnit(args.unit),
                rate=args.rate,
            )
            try:
                storage.add_service(service)
            except ValueError as exc:
                print(exc, file=sys.stderr)
                return 1
            print(f"Dodano usługę: {service.name} ({service.unit.value}) - {service.rate} zł")
            return 0
        if args.service_command == "list":
            services = storage.list_services()
            if not services:
                print("Brak zdefiniowanych usług")
            else:
                for service in services:
                    print(f"- {service.name}: {service.rate} zł / {service.unit.human_readable()}")
            return 0
        if args.service_command == "remove":
            if storage.remove_service(args.name):
                print(f"Usunięto usługę '{args.name}'")
            else:
                print(f"Nie znaleziono usługi '{args.name}'")
            return 0

    if args.command == "settings":
        settings = storage.get_settings()
        if args.settings_command == "show":
            print(json.dumps(settings.__dict__, ensure_ascii=False, indent=2))
            return 0
        if args.settings_command == "set-base":
            settings.base_address = args.address
            storage.update_settings(settings)
            print(f"Zapisano adres bazowy: {args.address}")
            return 0
        if args.settings_command == "set-travel-rate":
            settings.travel_rate_per_km = args.rate
            storage.update_settings(settings)
            print(f"Zapisano stawkę za kilometr: {args.rate} zł")
            return 0

    if args.command == "quote":
        settings = storage.get_settings()
        if not settings.base_address or settings.travel_rate_per_km is None:
            print("Ustaw adres bazowy i stawkę za kilometr przed wyceną", file=sys.stderr)
            return 2

        services = {srv.name.lower(): srv for srv in storage.list_services()}

        def provider(name: str) -> Optional[Service]:
            return services.get(name.lower())

        try:
            calculator = QuoteCalculator(
                service_provider=provider,
                geocoder=geocode,
                base_address=settings.base_address,
                travel_rate_per_km=float(settings.travel_rate_per_km),
            )
            result = calculator.calculate(
                service_name=args.service,
                quantity=args.quantity,
                client_address=args.client_address,
            )
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 3
        output = {
            "service_cost": result.service_cost,
            "travel_distance_km": result.travel_distance_km,
            "travel_cost": result.travel_cost,
            "total_cost": result.total_cost,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    return 0


def main() -> None:
    sys.exit(handle_args(sys.argv[1:]))


if __name__ == "__main__":
    main()
