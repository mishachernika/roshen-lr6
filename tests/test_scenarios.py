"""Пакет T3 — інтеграційні (сценарні) тести «сірого ящика».

Перевіряється співпраця calc_discount і process_order на наскрізних
сценаріях використання магазину: послідовні замовлення кількох клієнтів,
відновлення після відхиленого замовлення, синхронність знижки напряму
й через замовлення, а також демонстраційний сценарій main().
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


def fresh_stock():
    return {"Конфети": 50, "Торт": 20, "Шоколад": 100}


class ScenarioTests(unittest.TestCase):
    """Наскрізні сценарії: IT-01–IT-04."""

    def test_it01_two_customers_consistent_state(self):
        """IT-01 (R-04): послідовні замовлення двох клієнтів — суми і склад консистентні."""
        stock = fresh_stock()
        first = shop.process_order(
            {"Конфети": 3, "Торт": 2}, stock, PRICES, True)               # 680.8
        second = shop.process_order({"Шоколад": 4}, stock, PRICES, True)  # 329.8
        self.assertEqual(first, 680.8)
        self.assertEqual(second, 329.8)
        self.assertEqual(stock, {"Конфети": 47, "Торт": 18, "Шоколад": 96})

    def test_it02_rejected_order_leaves_stock_intact(self):
        """IT-02 (R-03): замовлення з відсутнім товаром не міняє склад; наступне успішне працює."""
        stock = fresh_stock()
        self.assertIsNone(shop.process_order({"Вафлі": 1, "Торт": 2}, stock, PRICES, False))
        self.assertEqual(stock, fresh_stock())
        self.assertEqual(
            shop.process_order({"Торт": 2, "Конфети": 1}, stock, PRICES, False), 475)
        self.assertEqual(stock["Торт"], 18)

    def test_it03_discount_consistent_between_interface_and_order(self):
        """IT-03 (R-01): знижка за карткою синхронна в calc_discount напряму й через замовлення."""
        stock = fresh_stock()
        order = {"Шоколад": 4, "Конфети": 5}                # сума 940
        direct = shop.calc_discount(940, True)
        via_order = shop.process_order(order, stock, PRICES, True)
        self.assertEqual(direct, via_order)                 # 940 · 0.92 = 864.8
        self.assertEqual(via_order, 864.8)

    def test_it04_demo_scenario_output(self):
        """IT-04 (R-06): демонстраційний сценарій main() виводить «До сплати: 680.8»."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            shop.main()
        self.assertEqual(buffer.getvalue().strip(), "До сплати: 680.8")


if __name__ == "__main__":
    unittest.main()
