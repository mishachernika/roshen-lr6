"""Візуальна оболонка (GUI) ПЗ магазину «Рошен» — реалізація ЛР6 на Tkinter.

Оболонка не змінює бізнес-логіку: усі розрахунки виконують протестовані
функції з roshen_shop.py (ЛР4–ЛР5) — calc_discount та process_order.
Запуск:  python gui.py
"""
import contextlib
import io
import os

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:  # headless-середовище без _tkinter: модуль все одно імпортується (тести, CI)
    tk = None

with contextlib.redirect_stdout(io.StringIO()):
    # імпорт roshen_shop виконує демонстраційний main() — вивід приховуємо
    import roshen_shop as shop

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HELP_PATH = os.path.join(BASE_DIR, "docs", "HELP_Магазин_Рошен.md")

PRICES = {"Конфети": 120, "Торт": 190, "Шоколад": 85}
STOCK = {"Конфети": 50, "Торт": 20, "Шоколад": 100}

# палітра та шрифти за ТЗ (docs/ТЗ_Магазин_Рошен.md, п. 5.1, таблиці 4–5)
CHERRY = "#B01E3C"    # основний: заголовок, панель меню, активна кнопка
GOLD = "#D9A441"      # акцентний: мітка картки, рамка панелі суми
PANEL_BG = "#FBF1DC"  # фон панелі суми
PANEL_FG = "#6B4A00"  # текст на панелі суми
TEXT = "#333333"
MUTED = "#666666"
FONT_UI = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI Semibold", 12)
FONT_MONO = ("Consolas", 10)  # у Tk розмір шрифту — ціле; візуально відповідає 9.5 pt у макеті


def validate_order(order, stock):
    """Повертає None для коректного замовлення або текст причини відмови (R-02, R-03, R-05)."""
    for name, qty in order.items():
        if name not in stock:
            return "Товар відсутній у прайс-листі"
        if stock[name] < qty:
            return "Недостатньо товару «%s»: залишок %d шт." % (name, stock[name])
        if qty <= 0:
            return "Кількість має бути більшою за нуль"
    return None


def discount_panel_text(total, is_member):
    """Текст панелі суми у форматі макета: сума → знижка → до сплати."""
    final = shop.calc_discount(total, is_member)
    rate = (1 - final / total) if total else 0.0
    return "Сума: %.2f  →  знижка %d%%  →  до сплати: %.2f грн" % (total, round(rate * 100), final), final


class ShopApp:
    """Головне вікно «Нове замовлення» (макет — рисунок 3 звіту ЛР6)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Магазин «Рошен» — нове замовлення")
        self.root.configure(bg="white")

        bar = tk.Frame(root, bg=CHERRY)
        bar.pack(fill="x")
        tk.Label(bar, text="Магазин «Рошен»", bg=CHERRY, fg="white",
                 font=FONT_HEAD).pack(side="left", padx=10, pady=6)
        tk.Button(bar, text="Довідка (F1)", bg=CHERRY, fg="white", bd=0,
                  font=FONT_UI, command=self.show_help).pack(side="right", padx=10)

        form = tk.Frame(root, bg="white")
        form.pack(padx=12, pady=10, fill="x")

        tk.Label(form, text="Товар:", bg="white", fg=TEXT, font=FONT_UI).grid(row=0, column=0, sticky="w")
        self.product = ttk.Combobox(form, values=list(PRICES), state="readonly", width=22, font=FONT_UI)
        self.product.current(1)  # «Торт»
        self.product.grid(row=0, column=1, sticky="w", pady=2)
        self.product.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Label(form, text="Кількість:", bg="white", fg=TEXT, font=FONT_UI).grid(row=1, column=0, sticky="w")
        self.qty = tk.Spinbox(form, from_=1, to=99, width=6, font=FONT_UI,
                              command=self.refresh)
        self.qty.grid(row=1, column=1, sticky="w", pady=2)
        self.stock_hint = tk.Label(form, text="", bg="white", fg=MUTED, font=FONT_UI)
        self.stock_hint.grid(row=1, column=2, sticky="w", padx=8)

        self.member = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Картка клієнта (+3 %)", variable=self.member,
                       bg="white", fg=TEXT, font=FONT_UI,
                       activebackground="white", command=self.refresh).grid(
            row=2, column=1, sticky="w", pady=2)

        self.panel = tk.Label(root, text="", bg=PANEL_BG, fg=PANEL_FG,
                              font=FONT_MONO, anchor="w", relief="solid", bd=2)
        self.panel.pack(fill="x", padx=12, pady=4)

        buttons = tk.Frame(root, bg="white")
        buttons.pack(pady=8)
        self.ok_btn = tk.Button(buttons, text="Оформити (Ctrl+Enter)", bg=CHERRY, fg="white",
                                font=FONT_UI, width=22, command=self.place_order)
        self.ok_btn.pack(side="left", padx=6)
        tk.Button(buttons, text="Скасувати (Esc)", bg="white", fg=TEXT, font=FONT_UI,
                  width=18, command=self.cancel).pack(side="left", padx=6)

        tk.Label(root, text="Склад:", bg="white", fg=TEXT, font=FONT_UI).pack(anchor="w", padx=12)
        self.tree = ttk.Treeview(root, columns=("stock",), show="headings", height=4)
        self.tree.heading("stock", text="Залишок, шт")
        self.tree.pack(padx=12, pady=(0, 10), fill="x")
        self.root.bind("<Control-Return>", lambda e: self.place_order())
        self.root.bind("<Escape>", lambda e: self.cancel())
        self.root.bind("<F1>", lambda e: self.show_help())

        self.refresh()
        self.refresh_stock()

    def refresh(self):
        name = self.product.get()
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        self.stock_hint.config(text="залишок: %d" % STOCK.get(name, 0))
        total = PRICES.get(name, 0) * qty
        text, _ = discount_panel_text(total, self.member.get())
        self.panel.config(text="  " + text)

    def refresh_stock(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, qty in STOCK.items():
            self.tree.insert("", "end", iid=name, values=("%s: %d" % (name, qty),))

    def place_order(self):
        name = self.product.get()
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        order = {name: qty}
        reason = validate_order(order, STOCK)
        if reason is not None:
            messagebox.showerror("Замовлення відхилено", reason + "\nСклад не змінено.")
            return
        final = shop.process_order(order, STOCK, PRICES, self.member.get())
        if final is None:
            messagebox.showerror("Замовлення відхилено", "Склад не змінено.")
            return
        messagebox.showinfo("Замовлення прийнято", "До сплати: %.2f грн" % final)
        self.refresh()
        self.refresh_stock()

    def cancel(self):
        self.qty.delete(0, "end")
        self.qty.insert(0, "1")
        self.member.set(False)
        self.refresh()

    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Довідка — ПЗ магазину «Рошен»")
        text = tk.Text(win, width=80, height=30, wrap="word", font=FONT_UI)
        scroll = ttk.Scrollbar(win, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        try:
            with open(HELP_PATH, encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except OSError:
            text.insert("1.0", "Файл довідки не знайдено: %s" % HELP_PATH)
        text.configure(state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")


def main():
    if tk is None:
        raise RuntimeError("Потрібен Python із підтримкою Tkinter (наприклад, пакет python3-tk)")
    root = tk.Tk()
    ShopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
