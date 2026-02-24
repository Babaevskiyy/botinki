from db import fetch_all


def get_categories():
    return fetch_all("SELECT CategoryID, CategoryName FROM category ORDER BY CategoryName")


def get_suppliers():
    return fetch_all("SELECT SupplierID, SupplierName FROM supplier ORDER BY SupplierName")


def get_manufacturers():
    return fetch_all("SELECT ManufacturerID, ManufacturerName FROM manufacturer ORDER BY ManufacturerName")


def get_units():
    return fetch_all("SELECT UnitID, UnitName FROM unit ORDER BY UnitName")


def get_statuses():
    return fetch_all("SELECT StatusID, StatusName FROM orderstatus ORDER BY StatusID")


def get_pickup_points():
    return fetch_all("""
        SELECT PickupPointID, PostalCode, City, Street, Building
        FROM pickuppoint
        ORDER BY City, Street, Building
    """)


def get_customers():
    return fetch_all("""
        SELECT UserID, UserSurname, UserName, UserPatronymic
        FROM `user`
        ORDER BY UserSurname, UserName
    """)