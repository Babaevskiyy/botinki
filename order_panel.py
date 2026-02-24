import tkinter as tk
from tkinter import ttk
import order_repo
from ui_utils import clear_tree, show_error, ask_confirm
from order_form import OrderForm


class OrdersPanel(ttk.Frame):
    def __init__(self, parent, role="manager"):
        super().__init__(parent)
        self.role = role 

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        tools = ttk.Frame(self)
        tools.pack(fill="x", pady=6)

        ttk.Button(tools, text="Обновить", command=self.refresh).pack(side="left", padx=6)

        if self.role == "admin":
            ttk.Button(tools, text="Добавить", command=self.add_order).pack(side="right", padx=6)
            ttk.Button(tools, text="Редакт.", command=self.edit_order).pack(side="right", padx=6)
            ttk.Button(tools, text="Удалить", command=self.delete_order).pack(side="right", padx=6)

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Заказы").pack(anchor="w")
        cols = ("id", "date", "deliv", "status", "customer", "pickup", "code", "sum")
        self.tree_orders = ttk.Treeview(left, columns=cols, show="headings", height=14)
        self.tree_orders.pack(fill="both", expand=True)

        headers = {
            "id": "№",
            "date": "Дата",
            "deliv": "Доставка",
            "status": "Статус",
            "customer": "Клиент",
            "pickup": "ПВЗ",
            "code": "Код",
            "sum": "Сумма",
        }
        widths = {"id": 60, "date": 90, "deliv": 90, "status": 110, "customer": 180,
                  "pickup": 240, "code": 70, "sum": 90}

        for c in cols:
            self.tree_orders.heading(c, text=headers[c])
            self.tree_orders.column(c, width=widths[c], anchor="w")

        self.tree_orders.column("id", anchor="center")
        self.tree_orders.column("code", anchor="center")
        self.tree_orders.column("sum", anchor="e")

        self.tree_orders.bind("<<TreeviewSelect>>", self._on_order_select)

        ttk.Label(right, text="Позиции заказа").pack(anchor="w")
        cols2 = ("art", "name", "qty", "price", "disc", "line")
        self.tree_items = ttk.Treeview(right, columns=cols2, show="headings", height=14)
        self.tree_items.pack(fill="both", expand=True)

        headers2 = {"art": "Артикул", "name": "Товар", "qty": "Кол-во",
                    "price": "Цена", "disc": "Скидка", "line": "Сумма"}
        widths2 = {"art": 120, "name": 260, "qty": 70, "price": 80, "disc": 70, "line": 90}
        for c in cols2:
            self.tree_items.heading(c, text=headers2[c])
            self.tree_items.column(c, width=widths2[c], anchor="w")

        self.tree_items.column("qty", anchor="center")
        self.tree_items.column("price", anchor="e")
        self.tree_items.column("disc", anchor="center")
        self.tree_items.column("line", anchor="e")

    def refresh(self):
        clear_tree(self.tree_orders)
        clear_tree(self.tree_items)

        rows = order_repo.list_orders()
        for r in rows:
            self.tree_orders.insert("", "end", values=(
                r["OrderID"],
                str(r["OrderDate"]),
                str(r["OrderDeliveryDate"]),
                r["StatusName"],
                r["CustomerFIO"],
                r["PickupAddress"],
                r["PickupCode"],
                f'{r["TotalSum"]:.2f}',
            ))

    def _selected_order_id(self):
        sel = self.tree_orders.selection()
        if not sel:
            return None
        vals = self.tree_orders.item(sel[0], "values")
        return int(vals[0])

    def _on_order_select(self, _):
        oid = self._selected_order_id()
        if not oid:
            return
        clear_tree(self.tree_items)
        items = order_repo.get_order_items(oid)
        for it in items:
            self.tree_items.insert("", "end", values=(
                it["ProductArticleNumber"],
                it["ProductName"],
                it["Qty"],
                f'{it["ProductPrice"]:.2f}',
                it["DiscountPercent"],
                f'{it["LineTotal"]:.2f}',
            ))

    def add_order(self):
        OrderForm(self, mode="add", on_saved=self.refresh)

    def edit_order(self):
        oid = self._selected_order_id()
        if not oid:
            show_error("Выбери заказ")
            return
        OrderForm(self, mode="edit", order_id=oid, on_saved=self.refresh)

    def delete_order(self):
        oid = self._selected_order_id()
        if not oid:
            show_error("Выбери заказ")
            return
        if not ask_confirm("Удаление", f"Удалить заказ #{oid}?"):
            return
        ok = order_repo.delete_order(oid)
        if not ok:
            show_error("Не удалось удалить заказ")
            return
        self.refresh()