from tkinter import ttk
from product_panel import ProductsPanel
from order_panel import OrdersPanel
from ui_utils import fio


class ManagerFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)

        ttk.Label(top, text="Панель менеджера", font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)
        self.lbl_user = ttk.Label(top, text="")
        self.lbl_user.pack(side="right", padx=8)
        ttk.Button(top, text="Выйти", command=self.app.logout).pack(side="right", padx=8)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        tab_products = ProductsPanel(nb, role="manager")
        tab_orders = OrdersPanel(nb, role="manager")

        nb.add(tab_products, text="Товары")
        nb.add(tab_orders, text="Заказы")

    def on_show(self):
        self.lbl_user.configure(text=fio(self.app.user))