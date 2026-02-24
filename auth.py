from db import fetch_one


def login_user(login, password):
    query = "SELECT * FROM `user` WHERE UserLogin=%s AND UserPassword=%s"
    return fetch_one(query, (login, password))