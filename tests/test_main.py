"""Проверки бизнес-правил; запускаются unittest или pytest."""

import unittest
from datetime import date, timedelta

from bookings import calculate_price, get_booking_status, is_slot_available


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 10, 22)

    def test_free_slot(self):
        self.assertTrue(is_slot_available(
            self.today, 14, 1, False, self.today))

    def test_past_date(self):
        self.assertFalse(is_slot_available(
            self.today - timedelta(days=1), 14, 1, False, self.today))

    def test_future_date(self):
        self.assertTrue(is_slot_available(
            self.today + timedelta(days=1), 14, 1, False, self.today))

    def test_busy_slot(self):
        self.assertFalse(is_slot_available(
            self.today, 14, 1, True, self.today))

    def test_working_hours_boundaries(self):
        for hour, duration, expected in (
            (9, 1, False), (10, 1, True), (19, 1, True),
            (20, 1, False), (19, 2, False), (14, 0, False),
            (14, -1, False),
        ):
            with self.subTest(hour=hour, duration=duration):
                self.assertEqual(is_slot_available(
                    self.today, hour, duration, False, self.today), expected)

    def test_student_discount(self):
        self.assertEqual(calculate_price(1500.0, True), 1350.0)

    def test_regular_price(self):
        self.assertEqual(calculate_price(1500.0, False), 1500.0)

    def test_rounding(self):
        self.assertEqual(calculate_price(999.99, True), 899.99)

    def test_zero_price(self):
        self.assertEqual(calculate_price(0, True), 0)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            calculate_price(-1, False)

    def test_confirmation(self):
        self.assertEqual(get_booking_status(" Анна ", True),
                         "Запись подтверждена для клиента Анна.")

    def test_empty_name(self):
        self.assertIn("не указано имя", get_booking_status("  ", True))

    def test_unavailable(self):
        self.assertIn("время недоступно", get_booking_status("Анна", False))


if __name__ == "__main__":
    unittest.main()
