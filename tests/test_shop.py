"""Модульні тести до roshen_shop.py: покривають шляхи, виділені в п. 3.3 звіту."""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
with contextlib.redirect_stdout(io.StringIO()):      # імпорт виконує main() — приховуємо вивід
    import roshen_shop as shop

PRICES = {"Конфети": 120, "Торт": 190, "Шоколад": 85}


class CalcDiscountTests(unittest.TestCase):
    def test_no_discount_below_500(self):
        self.assertEqual(shop.calc_discount(400, False), 400)

    def test_5_percent_from_500(self):
        self.assertEqual(shop.calc_discount(500, False), 475)

    def test_10_percent_from_1000(self):
        self.assertEqual(shop.calc_discount(1000, False), 900)

    def test_member_adds_3_percent(self):
        self.assertEqual(shop.calc_discount(740, True), 680.8)


class ProcessOrderTests(unittest.TestCase):
    def setUp(self):
        self.stock = {"Конфети": 50, "Торт": 20, "Шоколад": 100}

    def test_unknown_product_rejected(self):
        self.assertIsNone(shop.process_order({"Вафлі": 1}, self.stock, PRICES, False))

    def test_not_enough_stock_rejected_without_change(self):
        before = dict(self.stock)
        self.assertIsNone(shop.process_order({"Торт": 21}, self.stock, PRICES, False))
        self.assertEqual(self.stock, before)

    def test_valid_order_total_and_stock(self):
        result = shop.process_order({"Конфети": 3, "Торт": 2}, self.stock, PRICES, True)
        self.assertEqual(result, 680.8)
        self.assertEqual(self.stock["Конфети"], 47)
        self.assertEqual(self.stock["Торт"], 18)

    def test_empty_order(self):
        self.assertEqual(shop.process_order({}, self.stock, PRICES, False), 0)


if __name__ == "__main__":
    unittest.main()
