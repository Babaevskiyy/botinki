# Обувь – Информационная система магазина обуви

## Описание проекта

Информационная система ООО «Обувь» предназначена для автоматизации работы магазина обуви.

Система позволяет:

- вести учет товаров;
- выполнять поиск, сортировку и фильтрацию;
- просматривать фото и описание товара;
- оформлять и обрабатывать заказы;
- разграничивать доступ по ролям пользователей.

Проект реализован на Python с использованием:

- Tkinter (графический интерфейс)
- MySQL (база данных)
- mysql-connector-python (подключение к БД)
- Pillow (работа с изображениями)

---

## Требования

- Python 3.10 или выше  
- MySQL Workbench 8.0+  
- pip  

---

## Установка и запуск

### 1. Клонирование проекта

```bash
git clone <repository_url>
cd botinki
```

### 2. Создание виртуального окружения

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Если файла `requirements.txt` нет:

```bash
pip install mysql-connector-python Pillow
```

### 4. Создание базы данных

Запустить MySQL.

Создать базу данных:

```sql
CREATE DATABASE botinki_db;
```

Выполнить SQL-скрипт создания таблиц:

```sql
SOURCE sql/create_tables.sql;
```

### 5. Настройка подключения к БД

В файле `db.py` указать параметры подключения:

```python
host="localhost"
user="root"
password="ваш_пароль"
database="botinki_db"
```

### 6. Запуск приложения

```bash
python main.py
```

После запуска откроется форма авторизации.