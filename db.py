import os
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "botinki_db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "use_pure": True,          
    "autocommit": False,
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci",
}


def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print("Ошибка подключения к БД:", e)
        return None


def fetch_all(query, params=None):
    conn = connect_db()
    if conn is None:
        return []

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except Error as e:
        print("Ошибка запроса:", e)
        return []
    finally:
        cur.close()
        conn.close()


def fetch_one(query, params=None):
    conn = connect_db()
    if conn is None:
        return None

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchone()
    except Error as e:
        print("Ошибка запроса:", e)
        return None
    finally:
        cur.close()
        conn.close()


def execute(query, params=None, return_lastrowid=False):
    conn = connect_db()
    if conn is None:
        return None if return_lastrowid else False

    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        if return_lastrowid:
            return cur.lastrowid
        return True
    except Error as e:
        conn.rollback()
        print("Ошибка выполнения:", e)
        return None if return_lastrowid else False
    finally:
        cur.close()
        conn.close()


def executemany(query, seq_params):
    conn = connect_db()
    if conn is None:
        return False

    cur = conn.cursor()
    try:
        cur.executemany(query, seq_params)
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        print("Ошибка выполнения (many):", e)
        return False
    finally:
        cur.close()
        conn.close()