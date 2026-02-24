import tkinter as tk
from tkinter import messagebox
from datetime import datetime


def fio(user: dict):
    if not user:
        return "Гость"
    return f"{user.get('UserSurname','')} {user.get('UserName','')} {user.get('UserPatronymic','')}".strip()


def parse_date(s: str):
    s = s.strip()
    datetime.strptime(s, "%Y-%m-%d")
    return s


def ask_confirm(title, text):
    return messagebox.askyesno(title, text)


def show_error(text, title="Ошибка"):
    messagebox.showerror(title, text)


def show_info(text, title="Ок"):
    messagebox.showinfo(title, text)


def clear_tree(tree):
    for i in tree.get_children():
        tree.delete(i)