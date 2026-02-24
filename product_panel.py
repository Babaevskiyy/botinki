import os
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import lookup_repo
import product_repo
from ui_utils import clear_tree, show_error, ask_confirm
from product_form import ProductForm


class ProductsPanel(ttk.Frame):
    def __init__(self, parent, role="guest"):
        super().__init__(parent)
        self.role = role

        self.categories = lookup_repo.get_categories()

        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="Название")
        self.sort_dir_var = tk.StringVar(value="По возрастанию")
        self.category_var = tk.StringVar(value="Все")

        self.sort_map = {
            "Название": "name",
            "Цена": "price",
            "Остаток": "stock",
            "Скидка": "discount",
        }
        self.dir_map = {
            "По возрастанию": "ASC",
            "По убыванию": "DESC",
        }

        self.photos_dir = os.path.join(os.path.dirname(__file__), "assets", "photos")
        self.placeholder_name = "picture.png"
        self.placeholder_path = os.path.join(self.photos_dir, self.placeholder_name)

        self._img_ref = None
        self._search_after_id = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        if self.role in ("manager", "admin"):
            tools = ttk.Frame(self)
            tools.pack(fill="x", pady=6)

            ttk.Label(tools, text="Поиск:").pack(side="left", padx=6)
            self.search_entry = ttk.Entry(tools, textvariable=self.search_var, width=24)
            self.search_entry.pack(side="left")
            self.search_entry.bind("<KeyRelease>", self._on_search_typing)
            self.search_entry.bind("<Return>", lambda e: self.refresh())

            ttk.Label(tools, text="Категория:").pack(side="left", padx=8)
            cat_names = ["Все"] + [c["CategoryName"] for c in self.categories]
            self.cb_category = ttk.Combobox(
                tools, state="readonly", width=22, values=cat_names, textvariable=self.category_var
            )
            self.cb_category.pack(side="left")
            self.cb_category.bind("<<ComboboxSelected>>", lambda e: self.refresh())

            ttk.Label(tools, text="Сортировка:").pack(side="left", padx=8)
            self.cb_sort = ttk.Combobox(
                tools, state="readonly", width=14,
                values=list(self.sort_map.keys()),
                textvariable=self.sort_var
            )
            self.cb_sort.pack(side="left")
            self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh())

            self.cb_dir = ttk.Combobox(
                tools, state="readonly", width=16,
                values=list(self.dir_map.keys()),
                textvariable=self.sort_dir_var
            )
            self.cb_dir.pack(side="left", padx=6)
            self.cb_dir.bind("<<ComboboxSelected>>", lambda e: self.refresh())

            ttk.Button(tools, text="Обновить", command=self.refresh).pack(side="left", padx=10)

            if self.role == "admin":
                ttk.Button(tools, text="Добавить", command=self.add_product).pack(side="right", padx=6)
                ttk.Button(tools, text="Редакт.", command=self.edit_product).pack(side="right", padx=6)
                ttk.Button(tools, text="Удалить", command=self.delete_product).pack(side="right", padx=6)

        cols = ("art", "name", "cat", "sup", "man", "unit", "price", "disc", "stock", "photo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        self.tree.pack(fill="both", expand=True)

        headers = {
            "art": "Артикул",
            "name": "Название",
            "cat": "Категория",
            "sup": "Поставщик",
            "man": "Производитель",
            "unit": "Ед.",
            "price": "Цена",
            "disc": "Скидка",
            "stock": "Остаток",
            "photo": "Фото",
        }
        widths = {
            "art": 120, "name": 260, "cat": 140, "sup": 140, "man": 160, "unit": 60,
            "price": 80, "disc": 70, "stock": 80, "photo": 140
        }

        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor="w")

        self.tree.column("price", anchor="e")
        self.tree.column("disc", anchor="center")
        self.tree.column("stock", anchor="center")

        preview = ttk.Frame(self)
        preview.pack(fill="x", pady=6)

        ttk.Label(preview, text="Фото товара:").pack(side="left", padx=6)
        self.photo_label = ttk.Label(preview, text="Выберите товар")
        self.photo_label.pack(side="left", padx=10)

        desc_wrap = ttk.Frame(self)
        desc_wrap.pack(fill="both", padx=6, pady=(0, 8))

        ttk.Label(desc_wrap, text="Описание товара:").pack(anchor="w")

        self.desc_text = tk.Text(desc_wrap, height=4, wrap="word")
        self.desc_text.pack(fill="both", expand=True)
        self.desc_text.configure(state="disabled")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_search_typing(self, event=None):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(350, self.refresh)

    def refresh(self):
        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
            self._search_after_id = None

        clear_tree(self.tree)

        search = self.search_var.get().strip() if self.role in ("manager", "admin") else None

        category_id = None
        if self.role in ("manager", "admin") and self.category_var.get() != "Все":
            category_id = next(
                c["CategoryID"] for c in self.categories
                if c["CategoryName"] == self.category_var.get()
            )

        sort_key = None
        sort_dir = "ASC"
        if self.role in ("manager", "admin"):
            sort_key = self.sort_map.get(self.sort_var.get(), "name")
            sort_dir = self.dir_map.get(self.sort_dir_var.get(), "ASC")

        rows = product_repo.list_products(
            search=search,
            category_id=category_id,
            sort_key=sort_key,
            sort_dir=sort_dir
        )

        for r in rows:
            self.tree.insert("", "end", values=(
                r["ProductArticleNumber"],
                r["ProductName"],
                r["CategoryName"],
                r["SupplierName"],
                r["ManufacturerName"],
                r["UnitName"],
                f'{r["ProductPrice"]:.2f}',
                r["DiscountPercent"],
                r["StockQty"],
                r["PhotoFile"],
            ))

        self.photo_label.configure(image="", text="Выберите товар")
        self._img_ref = None
        self._set_description("")

    def _normalize_photo_name(self, photo_file):
        if photo_file is None:
            return None
        s = str(photo_file).strip()
        if not s or s.lower() in ("none", "null"):
            return None
        return s

    def _set_preview_image(self, path, text_if_error=""):
        try:
            img = Image.open(path)
            img.thumbnail((140, 140))
            tk_img = ImageTk.PhotoImage(img)
            self.photo_label.configure(image=tk_img, text="")
            self._img_ref = tk_img
        except Exception as e:
            self.photo_label.configure(image="", text=text_if_error or f"Ошибка фото: {e}")
            self._img_ref = None

    def _set_description(self, text):
        self.desc_text.configure(state="normal")
        self.desc_text.delete("1.0", "end")
        if text:
            self.desc_text.insert("1.0", str(text))
        self.desc_text.configure(state="disabled")

    def _on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return

        values = self.tree.item(sel[0], "values")
        art = values[0]
        photo_file = self._normalize_photo_name(values[-1])

        desc = ""
        try:
            row = product_repo.get_product(art)
            if row and "ProductDescription" in row and row["ProductDescription"] is not None:
                desc = row["ProductDescription"]
        except Exception:
            desc = ""
        self._set_description(desc)

        if photo_file is None:
            if os.path.exists(self.placeholder_path):
                self._set_preview_image(self.placeholder_path)
            else:
                self.photo_label.configure(image="", text="Нет фото")
                self._img_ref = None
            return

        path = os.path.join(self.photos_dir, photo_file)

        if not os.path.exists(path):
            if os.path.exists(self.placeholder_path):
                self._set_preview_image(self.placeholder_path)
            else:
                self.photo_label.configure(image="", text="Нет фото")
                self._img_ref = None
            return

        self._set_preview_image(path)

    def _selected_article(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        return vals[0]

    def add_product(self):
        ProductForm(self, mode="add", on_saved=self.refresh)

    def edit_product(self):
        art = self._selected_article()
        if not art:
            show_error("Выбери товар в таблице")
            return
        ProductForm(self, mode="edit", article=art, on_saved=self.refresh)

    def delete_product(self):
        art = self._selected_article()
        if not art:
            show_error("Выбери товар в таблице")
            return
        if not ask_confirm("Удаление", f"Удалить товар {art}?"):
            return
        ok = product_repo.delete_product(art)
        if not ok:
            show_error("Не удалось удалить (скорее всего товар связан с заказами)")
            return
        self.refresh()