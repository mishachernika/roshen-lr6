"""Тести візуальної оболонки gui.py (ЛР6) — headless: вікно Tk не створюється.

Перевіряється логіка, яку використовує форма замовлення (валідація причин
відмови, текст панелі суми) та зв'язок із протестованою бізнес-логікою
roshen_shop (calc_discount / process_order).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import gui  # gui сам приховує demo-вивід roshen_shop при імпорті


class ValidateOrderTests(unittest.TestCase):
    """Причини відмови відповідають таблиці 12 звіту (R-02, R-03, R-05)."""

    def setUp(self):
        self.stock = dict(gui.STOCK)

    def test_valid_order(self):
        self.assertIsNone(gui.validate_order({"Торт": 2}, self.stock))

    def test_unknown_product(self):
        self.assertIn("прайс-листі", gui.validate_order({"Вафлі": 1}, self.stock))

    def test_not_enough_stock(self):
        self.assertIn("Недостатньо", gui.validate_order({"Торт": 21}, self.stock))

    def test_zero_quantity(self):
        self.assertIn("більшою за нуль", gui.validate_order({"Торт": 0}, self.stock))


class WiringTests(unittest.TestCase):
    """Оболонка працює поверх тих самих функцій, що й консольний прототип."""

    def test_discount_logic_shared(self):
        self.assertEqual(gui.shop.calc_discount(740, True), 680.8)

    def test_order_logic_shared(self):
        stock = dict(gui.STOCK)
        final = gui.shop.process_order({"Конфети": 3, "Торт": 2}, stock, gui.PRICES, True)
        self.assertEqual(final, 680.8)
        self.assertEqual(stock["Конфети"], 47)

    def test_panel_text_matches_mockup(self):
        text, final = gui.discount_panel_text(740, True)
        self.assertEqual(final, 680.8)
        self.assertIn("знижка 8%", text)
        self.assertIn("680.80", text)

    def test_prices_match_product(self):
        self.assertEqual(gui.PRICES, {"Конфети": 120, "Торт": 190, "Шоколад": 85})


if __name__ == "__main__":
    unittest.main()
