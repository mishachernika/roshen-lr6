"""Візуальна оболонка (GUI) ПЗ магазину «Рошен» — реалізація ЛР6 на Tkinter.

Оболонка не змінює бізнес-логіку: усі розрахунки виконують протестовані
функції з roshen_shop.py (ЛР4–ЛР5) — calc_discount та process_order.
Дизайн — за макетами розділу 4 звіту ЛР6 (палітра #B01E3C / #D9A441 / #FBF1DC).
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
    style.configure("TButton", background=BG, foreground=TEXT, font=FONT_UI, padding=8)
    style.map("TButton", background=[("active", PANEL_BG)])
    style.configure("TCheckbutton", background=BG, foreground=TEXT, font=FONT_UI)
    style.configure("Panel.TLabel", background=PANEL_BG, foreground=PANEL_FG, font=FONT_MONO)
    style.configure("TCombobox", fieldbackground=BG, foreground=TEXT, font=FONT_UI)
    style.configure("Treeview", background=BG, fieldbackground=BG, foreground=TEXT, font=FONT_UI, rowheight=26)
    style.configure("Treeview.Heading", background=CHERRY, foreground="white", font=FONT_BOLD)
    style.map("Treeview", background=[("selected", PANEL_BG)], foreground=[("selected", PANEL_FG)])


class ShopApp:
    """Головне вікно «Нове замовлення» (макет — рисунок 3 звіту ЛР6)."""

    def __init__(self, root):
        self.root = root
        build_styles()
        root.title("Магазин «Рошен» — нове замовлення")
        root.configure(bg=BG)
        root.geometry("560x620")
        root.minsize(520, 580)

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
        tk.Button(header, text="Довідка (F1)", bg=CHERRY, fg="white", activebackground=CHERRY_DARK,
                  activeforeground="white", bd=0, font=FONT_UI, command=self.show_help).pack(side="right", padx=12)

        body = ttk.Frame(root, style="Card.TFrame")
        body.pack(fill="both", expand=True, padx=14, pady=12)
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text="Товар:", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.product = ttk.Combobox(body, values=list(PRICES), state="readonly", font=FONT_UI)
        self.product.current(1)  # «Торт»
        self.product.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=6)
        self.price_hint = ttk.Label(body, text="", style="Muted.TLabel")
        self.price_hint.grid(row=0, column=2, sticky="w", padx=8)
        self.product.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        ttk.Label(body, text="Кількість:", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.qty = tk.Spinbox(body, from_=1, to=99, width=8, font=FONT_UI, bg=BG, fg=TEXT,
                              buttonbackground=BG, command=self.refresh)
        self.qty.grid(row=1, column=1, sticky="w", padx=(8, 8), pady=6)
        self.stock_hint = ttk.Label(body, text="", style="Muted.TLabel")
        self.stock_hint.grid(row=1, column=2, sticky="w", padx=8)

        self.member = tk.BooleanVar(value=False)
        self.member_btn = ttk.Checkbutton(body, text="Картка клієнта (+3 %)", variable=self.member,
                                          style="TCheckbutton", command=self.refresh)
        self.member_btn.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=6)

        # панель суми (світло-золотий «чек»)
        self.panel = ttk.Label(body, text="", style="Panel.TLabel", anchor="w", padding=(10, 8))
        self.panel.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 6))

        buttons = ttk.Frame(body, style="Card.TFrame")
        buttons.grid(row=4, column=0, columnspan=3, pady=8)
        self.ok_btn = ttk.Button(buttons, text="Оформити (Ctrl+Enter)", style="Accent.TButton",
                                 command=self.place_order)
        self.ok_btn.pack(side="left", padx=(0, 8))
        self.cancel_btn = ttk.Button(buttons, text="Скасувати (Esc)", style="TButton", command=self.cancel)
        self.cancel_btn.pack(side="left")

        ttk.Label(body, text="Склад:", style="Field.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 4))
        self.tree = ttk.Treeview(body, columns=("name", "qty"), show="headings", height=5)
        self.tree.heading("name", text="Товар")
        self.tree.heading("qty", text="Залишок, шт")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("qty", width=120, anchor="center")
        self.tree.grid(row=6, column=0, columnspan=3, sticky="ew")

        # статус-бар із підказками (тексти — таблиця 15 звіту)
        self.hint = ttk.Label(root, text="", style="Muted.TLabel", anchor="w")
        self.hint.pack(fill="x", padx=14, pady=(0, 8))
        self._bind_hint(self.product, "Виберіть товар із прайс-листа")
        self._bind_hint(self.qty, "Додатне ціле, не більше залишку")
        self._bind_hint(self.member_btn, "Знижка постійного клієнта +3 %")
        self._bind_hint(self.ok_btn, "Списати товар зі складу та показати суму (Ctrl+Enter)")
        self._bind_hint(self.cancel_btn, "Закрити без змін (Esc)")

        root.bind("<Control-Return>", lambda e: self.place_order())
        root.bind("<Escape>", lambda e: self.cancel())
        root.bind("<F1>", lambda e: self.show_help())

        self._center()
        self.refresh()
        self.refresh_stock()

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
        total = PRICES.get(name, 0) * qty
        text, _ = discount_panel_text(total, self.member.get())
        self.panel.config(text="  " + text)

    def refresh_stock(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, qty in STOCK.items():
            self.tree.insert("", "end", iid=name, values=(name, qty))

    def place_order(self):
        name = self.product.get()
        try:
            qty = int(self.qty.get())
        except ValueError:
            qty = 0
        ok, result = submit_order({name: qty}, STOCK, PRICES, self.member.get())
        if not ok:
            messagebox.showerror("Замовлення відхилено", result + "\nСклад не змінено.", parent=self.root)
            return
        messagebox.showinfo("Замовлення прийнято", "До сплати: %.2f грн" % result, parent=self.root)
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
        win.configure(bg=BG)
        text = tk.Text(win, width=80, height=30, wrap="word", font=FONT_UI, bg=BG, fg=TEXT)
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
