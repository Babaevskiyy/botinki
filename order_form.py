import tkinter as tk
from tkinter import ttk
from ui_utils import show_error, show_info, parse_date
import lookup_repo
import order_repo
import product_repo


class OrderForm(tk.Toplevel):
    def __init__(self, parent, mode="add", order_id=None, on_saved=None):
        super().__init__(parent)
        self.mode = mode
        self.order_id = order_id
        self.on_saved = on_saved

        self.title("Заказ: добавление" if mode == "add" else "Заказ: редактирование")
        self.geometry("900x560")
        self.resizable(False, False)

        self.statuses = lookup_repo.get_statuses()
        self.points = lookup_repo.get_pickup_points()
        self.customers = lookup_repo.get_customers()

        self.items = [] 

        self._build_ui()

        if mode == "edit" and order_id:
            self._load(order_id)

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        pad = {"padx": 6, "pady": 4}

        ttk.Label(top, text="Клиент").grid(row=0, column=0, sticky="w", **pad)
        self.cb_customer = ttk.Combobox(
            top, state="readonly", width=35,
            values=[f'{c["UserSurname"]} {c["UserName"]} {c["UserPatronymic"]}'.strip() for c in self.customers]
        )
        self.cb_customer.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(top, text="Статус").grid(row=0, column=2, sticky="w", **pad)
        self.cb_status = ttk.Combobox(
            top, state="readonly", width=25,
            values=[s["StatusName"] for s in self.statuses]
        )
        self.cb_status.grid(row=0, column=3, sticky="w", **pad)

        ttk.Label(top, text="ПВЗ").grid(row=1, column=0, sticky="w", **pad)
        self.cb_point = ttk.Combobox(
            top, state="readonly", width=70,
            values=[f'{p["City"]}, {p["Street"]}, {p["Building"]} ({p["PostalCode"]})' for p in self.points]
        )
        self.cb_point.grid(row=1, column=1, columnspan=3, sticky="w", **pad)

        ttk.Label(top, text="Дата заказа (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", **pad)
        self.ent_date = ttk.Entry(top, width=18)
        self.ent_date.grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(top, text="Дата доставки (YYYY-MM-DD)").grid(row=2, column=2, sticky="w", **pad)
        self.ent_delivery = ttk.Entry(top, width=18)
        self.ent_delivery.grid(row=2, column=3, sticky="w", **pad)

        ttk.Label(top, text="Код выдачи").grid(row=3, column=0, sticky="w", **pad)
        self.ent_code = ttk.Entry(top, width=18)
        self.ent_code.grid(row=3, column=1, sticky="w", **pad)

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ttk.Label(mid, text="Позиции заказа").pack(anchor="w")

        self.tree = ttk.Treeview(mid, columns=("art", "name", "qty"), show="headings", height=12)
        self.tree.heading("art", text="Артикул")
        self.tree.heading("name", text="Товар")
        self.tree.heading("qty", text="Кол-во")
        self.tree.column("art", width=120)
        self.tree.column("name", width=600)
        self.tree.column("qty", width=80, anchor="center")
        self.tree.pack(fill="x", pady=6)

        btns = ttk.Frame(mid)
        btns.pack(fill="x")

        ttk.Button(btns, text="Добавить позицию", command=self._add_item).pack(side="left")
        ttk.Button(btns, text="Удалить позицию", command=self._remove_item).pack(side="left", padx=8)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=10)
        ttk.Button(bottom, text="Сохранить", command=self._save).pack(side="right", padx=6)
        ttk.Button(bottom, text="Отмена", command=self.destroy).pack(side="right")

    def _load(self, order_id):
        o = order_repo.get_order(order_id)
        if not o:
            show_error("Заказ не найден")
            self.destroy()
            return

        cust_str = next(
            (f'{c["UserSurname"]} {c["UserName"]} {c["UserPatronymic"]}'.strip()
             for c in self.customers if c["UserID"] == o["CustomerUserID"]),
            ""
        )
        status_str = next((s["StatusName"] for s in self.statuses if s["StatusID"] == o["StatusID"]), "")
        point_str = next(
            (f'{p["City"]}, {p["Street"]}, {p["Building"]} ({p["PostalCode"]})'
             for p in self.points if p["PickupPointID"] == o["PickupPointID"]),
            ""
        )

        self.cb_customer.set(cust_str)
        self.cb_status.set(status_str)
        self.cb_point.set(point_str)
        self.ent_date.insert(0, str(o["OrderDate"]))
        self.ent_delivery.insert(0, str(o["OrderDeliveryDate"]))
        self.ent_code.insert(0, str(o["PickupCode"]))

        items = order_repo.get_order_items(order_id)
        self.items = [{"ProductArticleNumber": it["ProductArticleNumber"], "Qty": it["Qty"]} for it in items]
        self._refresh_tree(items)

    def _refresh_tree(self, items_full=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if items_full is None:
            rows = []
            for it in self.items:
                p = product_repo.get_product(it["ProductArticleNumber"])
                name = p["ProductName"] if p else "???"
                rows.append({"ProductArticleNumber": it["ProductArticleNumber"], "ProductName": name, "Qty": it["Qty"]})
            items_full = rows

        for it in items_full:
            self.tree.insert("", "end", values=(it["ProductArticleNumber"], it["ProductName"], it["Qty"]))

    def _add_item(self):
        dlg = tk.Toplevel(self)
        dlg.title("Добавить позицию")
        dlg.geometry("520x170")
        dlg.resizable(False, False)

        products = product_repo.list_products()

        ttk.Label(dlg, text="Товар").pack(anchor="w", padx=10, pady=(10, 0))
        cb = ttk.Combobox(
            dlg, state="readonly", width=75,
            values=[f'{p["ProductArticleNumber"]} — {p["ProductName"]}' for p in products]
        )
        cb.pack(padx=10, pady=6)

        ttk.Label(dlg, text="Количество").pack(anchor="w", padx=10)
        ent_qty = ttk.Entry(dlg, width=10)
        ent_qty.pack(padx=10, pady=6)

        def ok():
            try:
                if not cb.get():
                    raise ValueError("Выбери товар")
                qty = int(ent_qty.get())
                if qty <= 0:
                    raise ValueError("Кол-во должно быть > 0")

                art = cb.get().split("—")[0].strip()
                found = False
                for it in self.items:
                    if it["ProductArticleNumber"] == art:
                        it["Qty"] += qty
                        found = True
                        break
                if not found:
                    self.items.append({"ProductArticleNumber": art, "Qty": qty})

                self._refresh_tree()
                dlg.destroy()
            except Exception as e:
                show_error(str(e))

        b = ttk.Frame(dlg)
        b.pack(fill="x", padx=10, pady=10)
        ttk.Button(b, text="Ок", command=ok).pack(side="right", padx=6)
        ttk.Button(b, text="Отмена", command=dlg.destroy).pack(side="right")

    def _remove_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        art = vals[0]
        self.items = [it for it in self.items if it["ProductArticleNumber"] != art]
        self._refresh_tree()

    def _save(self):
        try:
            if not (self.cb_customer.get() and self.cb_status.get() and self.cb_point.get()):
                raise ValueError("Заполни клиента/статус/ПВЗ")

            customer_id = next(
                c["UserID"] for c in self.customers
                if f'{c["UserSurname"]} {c["UserName"]} {c["UserPatronymic"]}'.strip() == self.cb_customer.get()
            )
            status_id = next(s["StatusID"] for s in self.statuses if s["StatusName"] == self.cb_status.get())
            point_id = next(
                p["PickupPointID"] for p in self.points
                if f'{p["City"]}, {p["Street"]}, {p["Building"]} ({p["PostalCode"]})' == self.cb_point.get()
            )

            order_date = parse_date(self.ent_date.get())
            deliv_date = parse_date(self.ent_delivery.get())
            code = int(self.ent_code.get())

            data = {
                "CustomerUserID": customer_id,
                "StatusID": status_id,
                "PickupPointID": point_id,
                "OrderDate": order_date,
                "OrderDeliveryDate": deliv_date,
                "PickupCode": code,
            }

            if self.mode == "add":
                new_id = order_repo.create_order(data, self.items)
                if not new_id:
                    show_error("Не удалось создать заказ")
                    return
                show_info(f"Создан заказ #{new_id}")
            else:
                ok = order_repo.update_order(self.order_id, data, self.items)
                if not ok:
                    show_error("Не удалось обновить заказ")
                    return
                show_info("Заказ обновлён")

            if self.on_saved:
                self.on_saved()
            self.destroy()

        except Exception as e:
            show_error(str(e))