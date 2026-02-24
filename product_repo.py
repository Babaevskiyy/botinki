from db import fetch_all, fetch_one, execute


SORT_MAP = {
    "name": "p.ProductName",
    "price": "p.ProductPrice",
    "stock": "p.StockQty",
    "discount": "p.DiscountPercent",
}


def list_products(search=None, category_id=None, sort_key=None, sort_dir="ASC"):
    base = """
        SELECT
            p.ProductArticleNumber,
            p.ProductName,
            p.ProductDescription,
            c.CategoryName,
            s.SupplierName,
            m.ManufacturerName,
            u.UnitName,
            p.ProductPrice,
            p.DiscountPercent,
            p.StockQty,
            p.PhotoFile
        FROM product p
        JOIN category c ON p.CategoryID=c.CategoryID
        JOIN supplier s ON p.SupplierID=s.SupplierID
        JOIN manufacturer m ON p.ManufacturerID=m.ManufacturerID
        JOIN unit u ON p.UnitID=u.UnitID
        WHERE 1=1
    """
    params = []

    if search:
        base += " AND (p.ProductName LIKE %s OR p.ProductArticleNumber LIKE %s)"
        like = f"%{search}%"
        params += [like, like]

    if category_id:
        base += " AND p.CategoryID = %s"
        params.append(category_id)

    if sort_key in SORT_MAP:
        direction = "DESC" if sort_dir == "DESC" else "ASC"
        base += f" ORDER BY {SORT_MAP[sort_key]} {direction}"
    else:
        base += " ORDER BY p.ProductName"

    return fetch_all(base, tuple(params))


def get_product(article):
    return fetch_one("""
        SELECT * FROM product WHERE ProductArticleNumber=%s
    """, (article,))


def add_product(data: dict):
    return execute("""
        INSERT INTO product
        (ProductArticleNumber, ProductName, ProductDescription, CategoryID, SupplierID,
         ManufacturerID, UnitID, ProductPrice, DiscountPercent, StockQty, PhotoFile)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["ProductArticleNumber"],
        data["ProductName"],
        data["ProductDescription"],
        data["CategoryID"],
        data["SupplierID"],
        data["ManufacturerID"],
        data["UnitID"],
        data["ProductPrice"],
        data["DiscountPercent"],
        data["StockQty"],
        data["PhotoFile"],
    ))


def update_product(article, data: dict):
    return execute("""
        UPDATE product SET
            ProductName=%s,
            ProductDescription=%s,
            CategoryID=%s,
            SupplierID=%s,
            ManufacturerID=%s,
            UnitID=%s,
            ProductPrice=%s,
            DiscountPercent=%s,
            StockQty=%s,
            PhotoFile=%s
        WHERE ProductArticleNumber=%s
    """, (
        data["ProductName"],
        data["ProductDescription"],
        data["CategoryID"],
        data["SupplierID"],
        data["ManufacturerID"],
        data["UnitID"],
        data["ProductPrice"],
        data["DiscountPercent"],
        data["StockQty"],
        data["PhotoFile"],
        article,
    ))


def delete_product(article):
    return execute("DELETE FROM product WHERE ProductArticleNumber=%s", (article,))