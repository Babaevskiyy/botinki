import os
import tkinter as tk
from tkinter import ttk

from login_window import LoginFrame
from guest_window import GuestFrame
from client_window import ClientFrame
from manager_window import ManagerFrame
from admin_window import AdminFrame


class BotinkiApp(tk.Tk):
    def __init__(self):
        super().__init__()

        base_dir = os.path.dirname(__file__)
        icon_ico = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_ico):
            self.iconbitmap(icon_ico)
            self.wm_iconbitmap(icon_ico)

        self.title("ООО «Обувь»")
        self.geometry("1280x650")
        self.minsize(1000, 600)

        self.user = None

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self._init_frames()

        self.show_frame("login")

    def _init_frames(self):
        self.frames["login"] = LoginFrame(self.container, self)
        self.frames["guest"] = GuestFrame(self.container, self)
        self.frames["client"] = ClientFrame(self.container, self)
        self.frames["manager"] = ManagerFrame(self.container, self)
        self.frames["admin"] = AdminFrame(self.container, self)

        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

    def set_user(self, user_dict):
        self.user = user_dict

    def logout(self):
        self.user = None
        self.show_frame("login")

    def open_by_role(self, user):
        rid = int(user["RoleID"])
        if rid == 1:
            self.show_frame("admin")
        elif rid == 2:
            self.show_frame("manager")
        else:
            self.show_frame("client")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()