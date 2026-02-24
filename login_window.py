import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from auth import login_user


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self._img_ref = None

        self._build_ui()

    def _build_ui(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        logo_path = os.path.join(assets_dir, "icon.png")

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((200, 200))
                tk_img = ImageTk.PhotoImage(img)

                logo_label = ttk.Label(self, image=tk_img)
                logo_label.pack(pady=(20, 5))

                self._img_ref = tk_img
            except Exception:
                pass

        ttk.Label(self, text="Авторизация", font=("Segoe UI", 14, "bold")).pack(pady=12)

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Логин").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.login_entry = ttk.Entry(form, width=30)
        self.login_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text="Пароль").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.password_entry = ttk.Entry(form, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=6, pady=6)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Войти", command=self.handle_login).pack(side="left", padx=6)
        ttk.Button(btns, text="Продолжить как гость", command=self.open_guest).pack(side="left", padx=6)

        self.login_entry.focus_set()

    def handle_login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        user = login_user(login, password)
        if not user:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        self.app.set_user(user)
        self.app.open_by_role(user)

    def open_guest(self):
        self.app.set_user(None)
        self.app.show_frame("guest")