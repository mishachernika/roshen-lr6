"""Пакет T2 — системні функціональні тести «чорного ящика».

Тестувальник подає замовлення через публічний інтерфейс
process_order() і порівнює суму до сплати та стан складу з очікуваннями
вимог R-01–R-05 (ЛР4, таблиця 11), не звертаючись до внутрішньої
структури модулів. Класи еквівалентності — за класами входів:
сума (пороги 500 і 1000), картка клієнта, кількість товару, склад замовлення.
"""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
with contextlib.redirect_stdout(io.StringIO()):      # імпорт виконує main()
    import roshen_shop as shop

PRICES = {"Конфети": 120, "Торт": 190, "Шоколад": 85}


class DiscountEquivalenceTests(unittest.TestCase):
    """Класи еквівалентності суми: пороги 500 (5 %) і 1000 (10 %); ST-01–ST-07 (R-01)."""

    def setUp(self):
        self.stock = {"Конфети": 50, "Торт": 20, "Шоколад": 100}

    def test_st01_no_discount_below_500(self):
        """ST-01 (R-01): сума 170 < 500 — без знижки."""
        self.assertEqual(
            shop.process_order({"Шоколад": 2}, self.stock, PRICES, False), 170)

    def test_st02_boundary_495_no_discount(self):
        """ST-02 (R-01): сума 495 — гранична під порогом, без знижки."""
        self.assertEqual(
            shop.process_order({"Шоколад": 3, "Конфети": 2}, self.stock, PRICES, False), 495)

    def test_st03_boundary_500_five_percent(self):
        """ST-03 (R-01): сума 500 рівно — знижка 5 %, до сплати 475."""
        self.assertEqual(
            shop.process_order({"Торт": 2, "Конфети": 1}, self.stock, PRICES, False), 475)

    def test_st04_sum_965_five_percent(self):
        """ST-04 (R-01): сума 965 — під порогом 10 %, знижка 5 %."""
        self.assertEqual(
            shop.process_order(
                {"Торт": 4, "Конфети": 1, "Шоколад": 1}, self.stock, PRICES, False), 916.75)
    def test_st05_boundary_1000_ten_percent(self):
        """ST-05 (R-01): сума 1000 рівно — знижка 10 %, до сплати 900."""
        self.assertEqual(
            shop.process_order({"Конфети": 2, "Торт": 4}, self.stock, PRICES, False), 900)

    def test_st06_above_1000_ten_percent(self):
        """ST-06 (R-01): сума 1410 — знижка 10 %, до сплати 1269."""
        self.assertEqual(
            shop.process_order(
                {"Конфети": 7, "Торт": 3}, self.stock, PRICES, False), 1269)

    def test_st07_member_adds_3_percent_to_5(self):
        """ST-07 (R-01): сума 965 + картка = знижка 8 %, до сплати 887.8."""
        self.assertEqual(
            shop.process_order(
                {"Торт": 4, "Конфети": 1, "Шоколад": 1}, self.stock, PRICES, True), 887.8)


class OrderRejectionTests(unittest.TestCase):
    """Негативні сценарії обробки замовлення: ST-08–ST-14."""

    def setUp(self):
        self.stock = {"Конфети": 50, "Торт": 20, "Шоколад": 100}

    def test_st08_unknown_product_rejected(self):
        """ST-08 (R-02): невідомий товар — замовлення відхилено, склад без змін."""
        self.assertIsNone(shop.process_order({"Вафлі": 3}, self.stock, PRICES, False))
        self.assertEqual(self.stock, {"Конфети": 50, "Торт": 20, "Шоколад": 100})

    def test_st09_empty_order_returns_zero(self):
        """ST-09 (R-01): порожнє замовлення — сума 0, склад без змін."""
        self.assertEqual(shop.process_order({}, self.stock, PRICES, True), 0)
        self.assertEqual(self.stock, {"Конфети": 50, "Торт": 20, "Шоколад": 100})

    def test_st10_quantity_equals_stock(self):
        """ST-10 (R-03): кількість дорівнює залишку — успіх, залишок 0."""
        self.assertEqual(shop.process_order({"Торт": 20}, self.stock, PRICES, False), 3420)
        self.assertEqual(self.stock["Торт"], 0)

    def test_st11_quantity_over_stock(self):
        """ST-11 (R-03): кількість = залишок + 1 — відхилено, склад без змін."""
        self.assertIsNone(shop.process_order({"Торт": 21}, self.stock, PRICES, False))
        self.assertEqual(self.stock["Торт"], 20)

    def test_st12_zero_quantity_rejected(self):
        """ST-12 (R-05): нульова кількість не приймається як коректне замовлення (D-02)."""
        self.assertIsNone(shop.process_order({"Торт": 0}, self.stock, PRICES, False))
        self.assertEqual(self.stock["Торт"], 20)

    def test_st13_negative_quantity_rejected(self):
        """ST-13 (R-05): від'ємна кількість відхиляється, залишок не змінюється (D-01)."""
        self.assertIsNone(shop.process_order({"Торт": -2}, self.stock, PRICES, False))
        self.assertEqual(self.stock, {"Конфети": 50, "Торт": 20, "Шоколад": 100})

    def test_st14_multi_position_order_total(self):
        """ST-14 (R-01): три позиції — сума 705, знижка 8 %, до сплати 648.6."""
        self.assertEqual(
            shop.process_order(
                {"Конфети": 2, "Торт": 2, "Шоколад": 1}, self.stock, PRICES, True), 648.6)
        self.assertEqual(
            self.stock, {"Конфети": 48, "Торт": 18, "Шоколад": 99})


if __name__ == "__main__":
    unittest.main()
