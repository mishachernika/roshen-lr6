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


class SubmitOrderTests(unittest.TestCase):
    """Логіка кнопки «Оформити» (submit_order): успіх списує склад, відмова — ні."""

    def test_success_writes_stock(self):
        stock = dict(gui.STOCK)
        ok, final = gui.submit_order({"Торт": 2}, stock, gui.PRICES, True)
        self.assertTrue(ok)
        self.assertEqual(final, 368.6)          # 380 грн, картка −3 %
        self.assertEqual(stock["Торт"], 18)

    def test_rejection_keeps_stock(self):
        stock = dict(gui.STOCK)
        ok, reason = gui.submit_order({"Торт": 21}, stock, gui.PRICES, False)
        self.assertFalse(ok)
        self.assertIn("Недостатньо", reason)
        self.assertEqual(stock["Торт"], 20)

    def test_zero_quantity_rejected(self):
        stock = dict(gui.STOCK)
        ok, reason = gui.submit_order({"Торт": 0}, stock, gui.PRICES, False)
        self.assertFalse(ok)
        self.assertIn("більшою за нуль", reason)
        self.assertEqual(stock["Торт"], 20)


class StockTabTests(unittest.TestCase):
    """Вкладка «Склад»: поповнення через restock."""

    def test_restock_ok(self):
        stock = dict(gui.STOCK)
        ok, left = gui.restock(stock, "Торт", 10)
        self.assertTrue(ok)
        self.assertEqual(left, 30)
        self.assertEqual(stock["Торт"], 30)

    def test_restock_unknown_product(self):
        ok, reason = gui.restock(dict(gui.STOCK), "Вафлі", 5)
        self.assertFalse(ok)
        self.assertIn("прайс-листі", reason)

    def test_restock_zero_keeps_stock(self):
        stock = dict(gui.STOCK)
        ok, reason = gui.restock(stock, "Торт", 0)
        self.assertFalse(ok)
        self.assertIn("більшою за нуль", reason)
        self.assertEqual(stock["Торт"], 20)


class CartAndHistoryTests(unittest.TestCase):
    """Вкладки «Нове замовлення» та «Чеки»: кошик, сума, історія, виручка."""

    def test_order_total(self):
        self.assertEqual(gui.order_total({"Торт": 2, "Шоколад": 1}, gui.PRICES), 465)

    def test_order_total_empty(self):
        self.assertEqual(gui.order_total({}, gui.PRICES), 0)

    def test_describe_order(self):
        self.assertEqual(gui.describe_order({"Торт": 4, "Шоколад": 8}), "Торт ×4; Шоколад ×8")

    def test_describe_order_empty(self):
        self.assertEqual(gui.describe_order({}), "—")

    def test_revenue_total(self):
        self.assertEqual(gui.revenue_total([{"final": 368.6}, {"final": 625.6}]), 994.2)

    def test_revenue_total_empty(self):
        self.assertEqual(gui.revenue_total([]), 0)

    def test_multi_item_cart_end_to_end(self):
        stock = dict(gui.STOCK)
        cart = {"Торт": 4, "Шоколад": 8}  # 760 + 680 = 1440 грн
        ok, final = gui.submit_order(cart, stock, gui.PRICES, True)
        self.assertTrue(ok)
        self.assertEqual(final, 1252.8)   # знижка 10 % (від 1000) + 3 % картка = 13 %
        self.assertEqual(stock["Торт"], 16)
        self.assertEqual(stock["Шоколад"], 92)


if __name__ == "__main__":
    unittest.main()
