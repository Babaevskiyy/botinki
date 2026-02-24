from db import fetch_all, fetch_one, execute, executemany


def list_orders(view_only=False):
    return fetch_all("""
        SELECT
            o.OrderID,
            o.OrderDate,
            o.OrderDeliveryDate,
            o.PickupCode,
            os.StatusName,
            CONCAT(u.UserSurname,' ',u.UserName,' ',u.UserPatronymic) AS CustomerFIO,
            CONCAT(pp.City, ', ', pp.Street, ', ', pp.Building, ' (', pp.PostalCode, ')') AS PickupAddress,
            (
                SELECT IFNULL(ROUND(SUM(oi.Qty * p.ProductPrice * (1 - p.DiscountPercent/100)), 2), 0)
                FROM orderitem oi
                JOIN product p ON oi.ProductArticleNumber = p.ProductArticleNumber
                WHERE oi.OrderID = o.OrderID
            ) AS TotalSum
        FROM `order` o
        JOIN orderstatus os ON o.StatusID = os.StatusID
        JOIN `user` u ON o.CustomerUserID = u.UserID
        JOIN pickuppoint pp ON o.PickupPointID = pp.PickupPointID
        ORDER BY o.OrderID DESC
    """)


def get_order(order_id):
    return fetch_one("SELECT * FROM `order` WHERE OrderID=%s", (order_id,))


def get_order_items(order_id):
    return fetch_all("""
        SELECT
            oi.ProductArticleNumber,
            p.ProductName,
            oi.Qty,
            p.ProductPrice,
            p.DiscountPercent,
            ROUND(oi.Qty * p.ProductPrice * (1 - p.DiscountPercent/100), 2) AS LineTotal
        FROM orderitem oi
        JOIN product p ON oi.ProductArticleNumber = p.ProductArticleNumber
        WHERE oi.OrderID=%s
        ORDER BY p.ProductName
    """, (order_id,))


def create_order(order_data: dict, items: list):
    new_id = execute("""
        INSERT INTO `order`
        (StatusID, OrderDate, OrderDeliveryDate, PickupPointID, CustomerUserID, PickupCode)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        order_data["StatusID"],
        order_data["OrderDate"],
        order_data["OrderDeliveryDate"],
        order_data["PickupPointID"],
        order_data["CustomerUserID"],
        order_data["PickupCode"],
    ), return_lastrowid=True)

    if not new_id:
        return None

    if items:
        ok = executemany("""
            INSERT INTO orderitem (OrderID, ProductArticleNumber, Qty)
            VALUES (%s,%s,%s)
        """, [(new_id, it["ProductArticleNumber"], it["Qty"]) for it in items])
        if not ok:
            return None

    return new_id


def update_order(order_id: int, order_data: dict, items: list):
    ok = execute("""
        UPDATE `order` SET
            StatusID=%s,
            OrderDate=%s,
            OrderDeliveryDate=%s,
            PickupPointID=%s,
            CustomerUserID=%s,
            PickupCode=%s
        WHERE OrderID=%s
    """, (
        order_data["StatusID"],
        order_data["OrderDate"],
        order_data["OrderDeliveryDate"],
        order_data["PickupPointID"],
        order_data["CustomerUserID"],
        order_data["PickupCode"],
        order_id
    ))
    if not ok:
        return False

    ok = execute("DELETE FROM orderitem WHERE OrderID=%s", (order_id,))
    if not ok:
        return False

    if items:
        ok = executemany("""
            INSERT INTO orderitem (OrderID, ProductArticleNumber, Qty)
            VALUES (%s,%s,%s)
        """, [(order_id, it["ProductArticleNumber"], it["Qty"]) for it in items])
        if not ok:
            return False

    return True


def delete_order(order_id: int):
    ok = execute("DELETE FROM orderitem WHERE OrderID=%s", (order_id,))
    if not ok:
        return False
    return execute("DELETE FROM `order` WHERE OrderID=%s", (order_id,))