from __future__ import annotations

import math
import unittest

from koszt_remontu.costs import QuoteCalculator
from koszt_remontu.models import PricingUnit, Service


class QuoteCalculatorTests(unittest.TestCase):
    def setUp(self) -> None:
        service = Service("Układanie płytek", PricingUnit.SQUARE_METER, 120)
        self.services = {service.name.lower(): service}

        coords = {
            "bazowy adres": (50.06143, 19.93658),
            "adres klienta": (52.22977, 21.01178),
        }

        def provider(name: str):
            return self.services.get(name.lower())

        def geocoder(address: str):
            key = address.lower()
            if key not in coords:
                raise ValueError("Nie znaleziono adresu")
            return coords[key]

        self.provider = provider
        self.geocoder = geocoder

    def test_calculate_quote(self) -> None:
        calculator = QuoteCalculator(
            service_provider=self.provider,
            geocoder=self.geocoder,
            base_address="bazowy adres",
            travel_rate_per_km=2.0,
        )

        result = calculator.calculate("Układanie płytek", 10, "adres klienta")

        self.assertTrue(math.isclose(result.service_cost, 1200.0, rel_tol=1e-3))
        self.assertGreater(result.travel_distance_km, 200)
        self.assertAlmostEqual(
            result.travel_cost,
            round(result.travel_distance_km * 2, 2),
            delta=0.02,
        )
        self.assertAlmostEqual(
            result.total_cost,
            round(result.service_cost + result.travel_cost, 2),
            delta=0.02,
        )

    def test_unknown_service_raises(self) -> None:
        calculator = QuoteCalculator(self.provider, self.geocoder, "bazowy adres", 1.0)
        with self.assertRaises(ValueError):
            calculator.calculate("Malowanie", 5, "adres klienta")

    def test_non_positive_quantity_raises(self) -> None:
        calculator = QuoteCalculator(self.provider, self.geocoder, "bazowy adres", 1.0)
        with self.assertRaises(ValueError):
            calculator.calculate("Układanie płytek", 0, "adres klienta")

    def test_accepts_direct_coordinates(self) -> None:
        calculator = QuoteCalculator(self.provider, self.geocoder, "50.06143,19.93658", 1.5)

        result = calculator.calculate("Układanie płytek", 5, "52.22977,21.01178")

        self.assertAlmostEqual(result.travel_distance_km, 252.66, delta=0.5)
        self.assertAlmostEqual(result.travel_cost, result.travel_distance_km * 1.5, delta=0.5)


if __name__ == "__main__":
    unittest.main()
