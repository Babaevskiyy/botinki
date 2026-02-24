from tkinter import ttk
from product_panel import ProductsPanel
from ui_utils import fio


class GuestFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)

        ttk.Label(top, text="Просмотр товаров (Гость)", font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)
        self.lbl_user = ttk.Label(top, text=fio(None))
        self.lbl_user.pack(side="right", padx=8)

        ttk.Button(top, text="Выйти", command=self.app.logout).pack(side="right", padx=8)

        ProductsPanel(self, role="guest").pack(fill="both", expand=True, padx=8, pady=8)

    def on_show(self):
        self.lbl_user.configure(text=fio(None))