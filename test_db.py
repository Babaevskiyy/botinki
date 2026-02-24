from db import connect_db

conn = connect_db()

if conn:
    print("Подключение к БД успешно")
    conn.close()
else:
    print("Не удалось подключиться к БД")