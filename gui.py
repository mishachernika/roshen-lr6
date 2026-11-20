"""
Графічна оболонка ПЗ магазину «Рошен» (ЛР6, варіант 13).

Оболонка не змінює бізнес-логіку: усі розрахунки виконують протестовані
функції з roshen_shop.py (ЛР4–ЛР5) — calc_discount та process_order.
Дизайн — за макетами розділу 4 звіту ЛР6 (палітра #B01E3C / #D9A441 / #FBF1DC).

Вкладки головного вікна:
  1. «Нове замовлення» — кошик, панель суми, оформлення чеку;
  2. «Склад» — залишки (підсвітка низьких) та поповнення складу;
  3. «Чеки» — історія оформлених замовлень і виручка за зміну.

Запуск:  python gui.py
"""
import contextlib
import io
import os
from datetime import datetime

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
LOW_STOCK = 10  # поріг «низький залишок» на вкладці «Склад»

# палітра та шрифти за ТЗ (docs/ТЗ_Магазин_Рошен.md, п. 5.1, таблиці 4–5)
CHERRY = "#B01E3C"    # основний: заголовок, активна кнопка, шапка таблиці
CHERRY_DARK = "#8F1730"
GOLD = "#D9A441"      # акцентний: рамка панелі суми
PANEL_BG = "#FBF1DC"  # фон панелі суми
PANEL_FG = "#6B4A00"  # текст на панелі суми
BG = "#FFFFFF"
TEXT = "#333333"
MUTED = "#666666"
FONT_UI = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEAD = ("Segoe UI Semibold", 13)
FONT_MONO = ("Consolas", 10)


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
    return "Сума: %.2f  →  знижка %d%%  →  ДО СПЛАТИ: %.2f грн" % (total, round(rate * 100), final), final


def submit_order(order, stock, prices, is_member):
    """Оформлення замовлення без GUI: (True, сума) або (False, причина відмови).

    Склад змінюється лише при успіху (R-02, R-03, R-05 — причини відмови).
    """
    reason = validate_order(order, stock)
    if reason is not None:
        return False, reason
    final = shop.process_order(order, stock, prices, is_member)
    if final is None:
        return False, "Замовлення відхилено"
    return True, final


def order_total(order, prices):
    """Сума кошика без знижки (вкладка «Нове замовлення»)."""
    return round(sum(prices[name] * qty for name, qty in order.items()), 2)


def restock(stock, name, qty):
    """Поповнення складу (вкладка «Склад»): (True, новий залишок) або (False, причина)."""
    if name not in stock:
        return False, "Товар відсутній у прайс-листі"
    if qty <= 0:
        return False, "Кількість має бути більшою за нуль"
    stock[name] += qty
    return True, stock[name]


def describe_order(order):
    """Компактний текст замовлення для вкладки «Чеки»: «Торт ×4; Шоколад ×8»."""
    return "; ".join("%s ×%d" % (name, qty) for name, qty in order.items()) or "—"


def revenue_total(history):
    """Виручка за зміну: сума полів final усіх чеків."""
    return round(sum(h["final"] for h in history), 2)


def build_styles():
    """Тема clam + наша палітра: усі кольори задані явно, щоб вигляд не залежав від системної теми."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=BG, foreground=TEXT, font=FONT_UI)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_UI)
    style.configure("Field.TLabel", background=BG, foreground=TEXT, font=FONT_BOLD)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_UI)
    style.configure("Header.TFrame", background=CHERRY)
    style.configure("Header.TLabel", background=CHERRY, foreground="white", font=FONT_HEAD)
    style.configure("Accent.TButton", background=CHERRY, foreground="white", font=FONT_BOLD, padding=8)
    style.map("Accent.TButton", background=[("active", CHERRY_DARK), ("pressed", CHERRY_DARK)])
    style.configure("Header.TButton", background=CHERRY_DARK, foreground="white", font=FONT_UI, padding=6)
    style.map("Header.TButton", background=[("active", CHERRY), ("pressed", CHERRY)],
                foreground=[("active", "white"), ("pressed", "white")])
    style.configure("TButton", background=BG, foreground=TEXT, font=FONT_UI, padding=8)
    style.map("TButton", background=[("active", PANEL_BG)])
    style.configure("TCheckbutton", background=BG, foreground=TEXT, font=FONT_UI)
    style.configure("Panel.TLabel", background=PANEL_BG, foreground=PANEL_FG, font=FONT_MONO)
    style.configure("TCombobox", fieldbackground=BG, foreground=TEXT, font=FONT_UI)
    style.configure("TNotebook", background=BG)
    style.configure("TNotebook.Tab", background=BG, foreground=TEXT, font=FONT_UI, padding=(12, 6))
    style.map("TNotebook.Tab", background=[("selected", PANEL_BG)], foreground=[("selected", PANEL_FG)])
    style.configure("Treeview", background=BG, fieldbackground=BG, foreground=TEXT, font=FONT_UI, rowheight=26)
    style.configure("Treeview.Heading", background=CHERRY, foreground="white", font=FONT_BOLD)
    style.map("Treeview", background=[("selected", PANEL_BG)], foreground=[("selected", PANEL_FG)])


class ShopApp:
    """Головне вікно з вкладками (макети — розділ 4 звіту ЛР6)."""

    def __init__(self, root):
        self.root = root
        build_styles()
        root.title("Магазин «Рошен» — каса")
        root.configure(bg=BG)
        root.geometry("720x660")
        root.minsize(660, 620)

        menubar = tk.Menu(root)
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="Вихід", accelerator="Alt+F4", command=root.destroy)
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Довідка (F1)", command=self.show_help)
        m_help.add_command(label="Про програму", command=self.show_about)
        menubar.add_cascade(label="Файл", menu=m_file)
        menubar.add_cascade(label="Довідка", menu=m_help)
        root.config(menu=menubar)

        # вишнева шапка
        header = ttk.Frame(root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Магазин «Рошен»", style="Header.TLabel").pack(side="left", padx=14, pady=10)
        ttk.Button(header, text="Довідка (F1)", style="Header.TButton",
                   command=self.show_help).pack(side="right", padx=12, pady=8)

        self.cart = {}     # кошик: {товар: кількість}
        self.history = []  # оформлені чеки: {"n", "time", "text", "rate", "final"}

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=12)
        self.tab_order = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_stock = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_receipts = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_order, text="Нове замовлення")
        self.notebook.add(self.tab_stock, text="Склад")
        self.notebook.add(self.tab_receipts, text="Чеки")
        self._build_order_tab()
        self._build_stock_tab()
        self._build_receipts_tab()

        # статус-бар із підказками (тексти — таблиця 15 звіту)
        self.hint = ttk.Label(root, text="", style="Muted.TLabel", anchor="w")
        self.hint.pack(fill="x", padx=14, pady=(0, 8))

        root.bind("<Control-Return>", lambda e: self.place_order())
        root.bind("<Escape>", lambda e: self.cancel())
        root.bind("<F1>", lambda e: self.show_help())

        self._center()
        self.refresh()
        self.refresh_cart()
        self.refresh_stock()
        self.refresh_history()

    # ---------- вкладка 1: нове замовлення ----------

    def _build_order_tab(self):
        tab = self.tab_order
        tab.columnconfigure(1, weight=1)

        form = ttk.Frame(tab, style="Card.TFrame")
        form.grid(row=0, column=0, sticky="n", padx=(0, 10), pady=4)

        ttk.Label(form, text="Товар:", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.product = ttk.Combobox(form, values=list(PRICES), state="readonly", font=FONT_UI, width=16)
        self.product.current(1)  # «Торт»
        self.product.grid(row=0, column=1, sticky="w", padx=(8, 8), pady=6)
        self.price_hint = ttk.Label(form, text="", style="Muted.TLabel")
        self.price_hint.grid(row=0, column=2, sticky="w", padx=8)
        self.product.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        ttk.Label(form, text="Кількість:", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.qty = tk.Spinbox(form, from_=1, to=99, width=8, font=FONT_UI, bg=BG, fg=TEXT,
                              buttonbackground=BG, command=self.refresh)
        self.qty.grid(row=1, column=1, sticky="w", padx=(8, 8), pady=6)
        self.stock_hint = ttk.Label(form, text="", style="Muted.TLabel")
        self.stock_hint.grid(row=1, column=2, sticky="w", padx=8)

        self.member = tk.BooleanVar(value=False)
        self.member_btn = ttk.Checkbutton(form, text="Картка клієнта (+3 %)", variable=self.member,
                                          style="TCheckbutton", command=self.refresh)
        self.member_btn.grid(row=2, column=0, columnspan=3, sticky="w", padx=(0, 8), pady=6)

        self.add_btn = ttk.Button(form, text="Додати в чек", style="TButton", command=self.add_to_cart)
        self.add_btn.grid(row=3, column=0, columnspan=2, sticky="w", padx=(0, 8), pady=6)

        # кошик (праворуч)
        cart_box = ttk.Frame(tab, style="Card.TFrame")
        cart_box.grid(row=0, column=1, sticky="nsew", pady=4)
        cart_box.columnconfigure(0, weight=1)
        ttk.Label(cart_box, text="Чек:", style="Field.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        self.cart_tree = ttk.Treeview(cart_box, columns=("name", "qty", "sum"), show="headings", height=6)
        self.cart_tree.heading("name", text="Товар")
        self.cart_tree.heading("qty", text="К-сть")
        self.cart_tree.heading("sum", text="Сума, грн")
        self.cart_tree.column("name", width=110, anchor="w")
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("sum", width=90, anchor="e")
        self.cart_tree.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 4))
        self.clear_btn = ttk.Button(cart_box, text="Очистити чек", style="TButton", command=self.clear_cart)
        self.clear_btn.grid(row=2, column=0, sticky="w", pady=(0, 4))

        # панель суми (світло-золотий «чек»)
        self.panel = ttk.Label(tab, text="", style="Panel.TLabel", anchor="w", padding=(10, 8))
        self.panel.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 6))

        buttons = ttk.Frame(tab, style="Card.TFrame")
        buttons.grid(row=2, column=0, columnspan=2, pady=8)
        self.ok_btn = ttk.Button(buttons, text="Оформити (Ctrl+Enter)", style="Accent.TButton",
                                 command=self.place_order)
        self.ok_btn.pack(side="left", padx=(0, 8))
        self.cancel_btn = ttk.Button(buttons, text="Скасувати (Esc)", style="TButton", command=self.cancel)
        self.cancel_btn.pack(side="left")

        self._bind_hint(self.product, "Виберіть товар із прайс-листа")
        self._bind_hint(self.qty, "Додатне ціле, не більше залишку")
        self._bind_hint(self.member_btn, "Знижка постійного клієнта +3 %")
        self._bind_hint(self.add_btn, "Додати вибраний товар у кошик")
        self._bind_hint(self.clear_btn, "Очистити кошик без оформлення")
        self._bind_hint(self.ok_btn, "Оформити весь чек: списати склад і показати суму (Ctrl+Enter)")
        self._bind_hint(self.cancel_btn, "Очистити форму і кошик без змін (Esc)")

    # ---------- вкладка 2: склад ----------

    def _build_stock_tab(self):
        tab = self.tab_stock
        tab.columnconfigure(0, weight=1)
        ttk.Label(tab, text="Залишки на складі:", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.stock_tree = ttk.Treeview(tab, columns=("name", "qty", "status"), show="headings", height=6)
        self.stock_tree.heading("name", text="Товар")
        self.stock_tree.heading("qty", text="Залишок, шт")
        self.stock_tree.heading("status", text="Статус")
        self.stock_tree.column("name", width=160, anchor="w")
        self.stock_tree.column("qty", width=110, anchor="center")
        self.stock_tree.column("status", width=140, anchor="w")
        self.stock_tree.tag_configure("low", foreground=CHERRY)
        self.stock_tree.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 8))

        ttk.Label(tab, text="Поповнити:", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.restock_product = ttk.Combobox(tab, values=list(PRICES), state="readonly", font=FONT_UI, width=16)
        self.restock_product.current(0)
        self.restock_product.grid(row=2, column=1, sticky="w", padx=(8, 8), pady=6)
        self.restock_qty = tk.Spinbox(tab, from_=1, to=999, width=6, font=FONT_UI, bg=BG, fg=TEXT,
                                      buttonbackground=BG)
        self.restock_qty.grid(row=2, column=2, sticky="w", pady=6)
        self.restock_btn = ttk.Button(tab, text="Поповнити складу", style="Accent.TButton",
                                      command=self.do_restock)
        self.restock_btn.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 6))
        self._bind_hint(self.restock_btn, "Додати вибрану кількість товару на склад")

    # ---------- вкладка 3: чеки ----------

    def _build_receipts_tab(self):
        tab = self.tab_receipts
        tab.columnconfigure(0, weight=1)
        ttk.Label(tab, text="Оформлені замовлення:", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.hist_tree = ttk.Treeview(tab, columns=("n", "time", "items", "rate", "final"),
                                      show="headings", height=9)
        self.hist_tree.heading("n", text="№")
        self.hist_tree.heading("time", text="Час")
        self.hist_tree.heading("items", text="Замовлення")
        self.hist_tree.heading("rate", text="Знижка")
        self.hist_tree.heading("final", text="До сплати, грн")
        self.hist_tree.column("n", width=40, anchor="center")
        self.hist_tree.column("time", width=80, anchor="center")
        self.hist_tree.column("items", width=260, anchor="w")
        self.hist_tree.column("rate", width=70, anchor="center")
        self.hist_tree.column("final", width=110, anchor="e")
        self.hist_tree.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.revenue = ttk.Label(tab, text="", style="Panel.TLabel", anchor="w", padding=(10, 8))
        self.revenue.grid(row=2, column=0, sticky="ew")

    # ---------- спільні дії ----------

    def _center(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry("+%d+%d" % (x, y))

    def _bind_hint(self, widget, text):
        widget.bind("<Enter>", lambda e: self.hint.config(text=text))
        widget.bind("<Leave>", lambda e: self.hint.config(text=""))

    def refresh(self):
        name = self.product.get()
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        self.price_hint.config(text="ціна: %d грн" % PRICES.get(name, 0))
        self.stock_hint.config(text="залишок: %d шт" % STOCK.get(name, 0))
        total = order_total(self.cart, PRICES)
        text, _ = discount_panel_text(total, self.member.get())
        self.panel.config(text="  " + text)

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        for name, qty in self.cart.items():
            self.cart_tree.insert("", "end", iid=name, values=(name, qty, "%.2f" % (qty * PRICES[name])))

    def refresh_stock(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        for name, qty in STOCK.items():
            low = qty < LOW_STOCK
            self.stock_tree.insert("", "end", iid=name, values=(name, qty, "низький залишок" if low else "ок"),
                                   tags=("low",) if low else ())

    def refresh_history(self):
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)
        for h in self.history:
            self.hist_tree.insert("", "end", iid=str(h["n"]),
                                  values=(h["n"], h["time"], h["text"], "%d%%" % h["rate"], "%.2f" % h["final"]))
        self.revenue.config(text="  Виручка за зміну: %.2f грн  (чеків: %d)" % (revenue_total(self.history), len(self.history)))

    def add_to_cart(self):
        name = self.product.get()
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        if qty <= 0:
            messagebox.showwarning("Некоректна кількість", "Кількість має бути більшою за нуль.", parent=self.root)
            return
        self.cart[name] = self.cart.get(name, 0) + qty
        self.refresh_cart()
        self.refresh()

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart()
        self.refresh()

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Чек порожній", "Додайте товари в чек кнопкою «Додати в чек».", parent=self.root)
            return
        ok, result = submit_order(dict(self.cart), STOCK, PRICES, self.member.get())
        if not ok:
            messagebox.showerror("Замовлення відхилено", result + "\nСклад не змінено.", parent=self.root)
            return
        total = order_total(self.cart, PRICES)
        _, final = discount_panel_text(total, self.member.get())
        rate = round((1 - final / total) * 100) if total else 0
        entry = {"n": len(self.history) + 1,
                 "time": datetime.now().strftime("%H:%M:%S"),
                 "text": describe_order(self.cart),
                 "rate": rate,
                 "final": final}
        self.history.append(entry)
        messagebox.showinfo("Замовлення №%d прийнято" % entry["n"],
                            "До сплати: %.2f грн" % final, parent=self.root)
        self.cart.clear()
        self.refresh_cart()
        self.refresh()
        self.refresh_stock()
        self.refresh_history()

    def cancel(self):
        self.qty.delete(0, "end")
        self.qty.insert(0, "1")
        self.member.set(False)
        self.clear_cart()

    def do_restock(self):
        name = self.restock_product.get()
        try:
            qty = int(self.restock_qty.get())
        except ValueError:
            qty = 0
        ok, result = restock(STOCK, name, qty)
        if not ok:
            messagebox.showerror("Поповнення відхилено", result, parent=self.root)
            return
        messagebox.showinfo("Склад поповнено", "«%s»: залишок %d шт." % (name, result), parent=self.root)
        self.refresh_stock()
        self.refresh()

    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Довідка — ПЗ магазину «Рошен»")
        win.configure(bg=BG)
        win.geometry("620x520")
        text = tk.Text(win, wrap="word", font=FONT_UI, bg=BG, fg=TEXT, padx=12, pady=10)
        scroll = ttk.Scrollbar(win, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.tag_configure("h1", font=FONT_HEAD, foreground=CHERRY, spacing1=6, spacing3=6)
        text.tag_configure("h2", font=FONT_BOLD, foreground=CHERRY_DARK, spacing1=10, spacing3=4)
        text.tag_configure("code", font=FONT_MONO, background=PANEL_BG)
        try:
            with open(HELP_PATH, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            content = "Файл довідки не знайдено: %s" % HELP_PATH
        in_code = False
        for line in content.splitlines():
            if line.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                text.insert("end", line + "\n", "code")
            elif line.startswith("## "):
                text.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("# "):
                text.insert("end", line[2:] + "\n", "h1")
            else:
                text.insert("end", line + "\n")
        text.configure(state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def show_about(self):
        messagebox.showinfo(
            "Про програму",
            "ПЗ магазину «Рошен» (варіант 13).\n"
            "Версія 1.0, спіраль ЛР6. Автор: Чернік Михайло, група ІПЗ-41.\n"
            "Бізнес-логіка: roshen_shop.py (протестована, ЛР4–ЛР5).",
            parent=self.root)


def main():
    if tk is None:
        raise RuntimeError("Потрібен Python із підтримкою Tkinter (наприклад, пакет python3-tk)")
    root = tk.Tk()
    ShopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
