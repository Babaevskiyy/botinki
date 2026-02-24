import tkinter as tk
from tkinter import ttk
from ui_utils import show_error, show_info
import lookup_repo
import product_repo


class ProductForm(tk.Toplevel):
    def __init__(self, parent, mode="add", article=None, on_saved=None):
        super().__init__(parent)
        self.mode = mode
        self.article = article
        self.on_saved = on_saved

        self.title("Товар: добавление" if mode == "add" else "Товар: редактирование")
        self.geometry("650x520")
        self.resizable(False, False)

        self.categories = lookup_repo.get_categories()
        self.suppliers = lookup_repo.get_suppliers()
        self.manufacturers = lookup_repo.get_manufacturers()
        self.units = lookup_repo.get_units()

        self._build_ui()

        if mode == "edit" and article:
            self._load(article)

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Артикул").grid(row=0, column=0, sticky="w", **pad)
        self.ent_article = ttk.Entry(frm, width=30)
        self.ent_article.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Название").grid(row=1, column=0, sticky="w", **pad)
        self.ent_name = ttk.Entry(frm, width=60)
        self.ent_name.grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Описание").grid(row=2, column=0, sticky="nw", **pad)
        self.txt_desc = tk.Text(frm, width=62, height=6)
        self.txt_desc.grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Категория").grid(row=3, column=0, sticky="w", **pad)
        self.cb_cat = ttk.Combobox(frm, state="readonly", width=40,
                                   values=[c["CategoryName"] for c in self.categories])
        self.cb_cat.grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Поставщик").grid(row=4, column=0, sticky="w", **pad)
        self.cb_sup = ttk.Combobox(frm, state="readonly", width=40,
                                   values=[s["SupplierName"] for s in self.suppliers])
        self.cb_sup.grid(row=4, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Производитель").grid(row=5, column=0, sticky="w", **pad)
        self.cb_man = ttk.Combobox(frm, state="readonly", width=40,
                                   values=[m["ManufacturerName"] for m in self.manufacturers])
        self.cb_man.grid(row=5, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Ед. изм.").grid(row=6, column=0, sticky="w", **pad)
        self.cb_unit = ttk.Combobox(frm, state="readonly", width=40,
                                    values=[u["UnitName"] for u in self.units])
        self.cb_unit.grid(row=6, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Цена").grid(row=7, column=0, sticky="w", **pad)
        self.ent_price = ttk.Entry(frm, width=20)
        self.ent_price.grid(row=7, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Скидка %").grid(row=8, column=0, sticky="w", **pad)
        self.ent_disc = ttk.Entry(frm, width=20)
        self.ent_disc.grid(row=8, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Остаток").grid(row=9, column=0, sticky="w", **pad)
        self.ent_stock = ttk.Entry(frm, width=20)
        self.ent_stock.grid(row=9, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Фото (файл)").grid(row=10, column=0, sticky="w", **pad)
        self.ent_photo = ttk.Entry(frm, width=40)
        self.ent_photo.grid(row=10, column=1, sticky="w", **pad)

        btns = ttk.Frame(frm)
        btns.grid(row=11, column=0, columnspan=2, sticky="e", pady=12)

        ttk.Button(btns, text="Сохранить", command=self._save).pack(side="right", padx=6)
        ttk.Button(btns, text="Отмена", command=self.destroy).pack(side="right")

        if self.mode == "edit":
            self.ent_article.configure(state="disabled")

    def _load(self, article):
        p = product_repo.get_product(article)
        if not p:
            show_error("Товар не найден")
            self.destroy()
            return

        self.ent_article.insert(0, p["ProductArticleNumber"])
        self.ent_name.insert(0, p["ProductName"])
        self.txt_desc.insert("1.0", p.get("ProductDescription") or "")

        cat_name = next((c["CategoryName"] for c in self.categories if c["CategoryID"] == p["CategoryID"]), "")
        sup_name = next((s["SupplierName"] for s in self.suppliers if s["SupplierID"] == p["SupplierID"]), "")
        man_name = next((m["ManufacturerName"] for m in self.manufacturers if m["ManufacturerID"] == p["ManufacturerID"]), "")
        unit_name = next((u["UnitName"] for u in self.units if u["UnitID"] == p["UnitID"]), "")

        self.cb_cat.set(cat_name)
        self.cb_sup.set(sup_name)
        self.cb_man.set(man_name)
        self.cb_unit.set(unit_name)

        self.ent_price.insert(0, str(p["ProductPrice"]))
        self.ent_disc.insert(0, str(p["DiscountPercent"]))
        self.ent_stock.insert(0, str(p["StockQty"]))
        self.ent_photo.insert(0, p.get("PhotoFile") or "")

    def _save(self):
        try:
            article = self.ent_article.get().strip()
            name = self.ent_name.get().strip()
            desc = self.txt_desc.get("1.0", "end").strip()

            if not article or not name:
                raise ValueError("Артикул и название обязательны")

            cat = self.cb_cat.get()
            sup = self.cb_sup.get()
            man = self.cb_man.get()
            unit = self.cb_unit.get()

            if not (cat and sup and man and unit):
                raise ValueError("Выбери категорию/поставщика/производителя/ед.изм.")

            cat_id = next(c["CategoryID"] for c in self.categories if c["CategoryName"] == cat)
            sup_id = next(s["SupplierID"] for s in self.suppliers if s["SupplierName"] == sup)
            man_id = next(m["ManufacturerID"] for m in self.manufacturers if m["ManufacturerName"] == man)
            unit_id = next(u["UnitID"] for u in self.units if u["UnitName"] == unit)

            price = float(self.ent_price.get().replace(",", "."))
            disc = int(self.ent_disc.get())
            stock = int(self.ent_stock.get())
            photo = self.ent_photo.get().strip()

            if disc < 0 or disc > 100:
                raise ValueError("Скидка должна быть 0..100")

            data = {
                "ProductArticleNumber": article,
                "ProductName": name,
                "ProductDescription": desc,
                "CategoryID": cat_id,
                "SupplierID": sup_id,
                "ManufacturerID": man_id,
                "UnitID": unit_id,
                "ProductPrice": price,
                "DiscountPercent": disc,
                "StockQty": stock,
                "PhotoFile": photo,
            }

            if self.mode == "add":
                ok = product_repo.add_product(data)
            else:
                ok = product_repo.update_product(self.article, data)

            if not ok:
                show_error("Не удалось сохранить (возможно, артикул уже существует или FK)")
                return

            show_info("Сохранено")
            if self.on_saved:
                self.on_saved()
            self.destroy()

        except Exception as e:
            show_error(str(e))