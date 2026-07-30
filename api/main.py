from fastapi import FastAPI, HTTPException, Header
import sqlite3
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="Olist Interview API",
    description="REST API for Data Analytics Interview",
    version="2.1"
)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "olist.db"

API_KEY = "candidate-test-2026"

print(f"Database Path: {DB_PATH}")
print(f"Database Exists: {DB_PATH.exists()}")


# ----------------------------------------------------
# Authentication
# ----------------------------------------------------

def verify_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


# ----------------------------------------------------
# Database Connection
# ----------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH)


# ----------------------------------------------------
# Convert dataframe to JSON-safe format
# ----------------------------------------------------

def dataframe_to_records(df):
    # Replace NaN, +Infinity, and -Infinity with None,
    # since JSON does not support any of these values.
    df = df.replace([float("inf"), float("-inf")], None)
    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


# ----------------------------------------------------
# Generic Table Loader
# ----------------------------------------------------

def get_table(table: str, page: int = 1, limit: int = 100):

    try:

        conn = get_connection()

        offset = (page - 1) * limit

        total = int(
            pd.read_sql(
                f"SELECT COUNT(*) as total FROM {table}",
                conn
            ).iloc[0]["total"]
        )

        df = pd.read_sql(
            f"""
            SELECT *
            FROM {table}
            LIMIT {limit}
            OFFSET {offset}
            """,
            conn
        )

        conn.close()

        return {
            "page": int(page),
            "limit": int(limit),
            "total_records": total,
            "returned_records": int(len(df)),
            "has_next": bool(offset + limit < total),
            "data": dataframe_to_records(df)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------------------------------
# Home
# ----------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to Olist Interview API",
        "version": "2.1"
    }


# ----------------------------------------------------
# Customers
# ----------------------------------------------------
@app.get("/customers")
def customers(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("customers", page, limit)
@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM customers WHERE customer_id = ?",
        conn,
        params=(customer_id,)
    )

    conn.close()

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return dataframe_to_records(df)[0]

# ----------------------------------------------------
# Orders
# ----------------------------------------------------

@app.get("/orders")
def orders(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("orders", page, limit)
@app.get("/orders/{order_id}")
def get_order(
    order_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM orders WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    conn.close()

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return dataframe_to_records(df)[0]

# ----------------------------------------------------
# Order Items
# ----------------------------------------------------

@app.get("/order_items")
def order_items(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("order_items", page, limit)


# ----------------------------------------------------
# Payments
# ----------------------------------------------------

@app.get("/payments")
def payments(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("payments", page, limit)


# ----------------------------------------------------
# Products
# ----------------------------------------------------

@app.get("/products")
def products(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("products", page, limit)
@app.get("/products/{product_id}")
def get_product(
    product_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM products WHERE product_id = ?",
        conn,
        params=(product_id,)
    )

    conn.close()

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return dataframe_to_records(df)[0]


# ----------------------------------------------------
# Sellers
# ----------------------------------------------------

@app.get("/sellers")
def sellers(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("sellers", page, limit)


# ----------------------------------------------------
# Reviews
# ----------------------------------------------------

@app.get("/reviews")
def reviews(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("reviews", page, limit)


# ----------------------------------------------------
# Geolocation
# ----------------------------------------------------

@app.get("/geolocation")
def geolocation(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("geolocation", page, limit)


# ----------------------------------------------------
# Category Translation
# ----------------------------------------------------

@app.get("/categories")
def categories(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    df = pd.read_sql(
        "SELECT DISTINCT product_category_name FROM products WHERE product_category_name IS NOT NULL",
        conn
    )

    conn.close()

    return dataframe_to_records(df)


@app.get("/categories/translation")
def categories_translation(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("category_translation", page, limit)
@app.get("/analytics/top-selling-products")
def top_selling_products(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            product_id,
            COUNT(*) AS units_sold
        FROM order_items
        GROUP BY product_id
        ORDER BY units_sold DESC
        LIMIT 10
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/top-revenue-products")
def top_revenue_products(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            product_id,
            SUM(price) AS total_revenue
        FROM order_items
        GROUP BY product_id
        ORDER BY total_revenue DESC
        LIMIT 10
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/monthly-revenue")
def monthly_revenue(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            strftime('%Y-%m', o.order_purchase_timestamp) AS month,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY month
        ORDER BY month
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/revenue-by-state")
def revenue_by_state(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            c.customer_state AS state,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY total_revenue DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/revenue-by-category")
def revenue_by_category(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            p.product_category_name AS category,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY total_revenue DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/average-order-value")
def average_order_value(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT AVG(order_total) AS average_order_value
        FROM (
            SELECT
                order_id,
                SUM(price) AS order_total
            FROM order_items
            GROUP BY order_id
        )
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/average-basket-size")
def average_basket_size(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT AVG(item_count) AS average_basket_size
        FROM (
            SELECT
                order_id,
                COUNT(*) AS item_count
            FROM order_items
            GROUP BY order_id
        )
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/average-delivery-time")
def average_delivery_time(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            AVG(julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) AS average_delivery_days
        FROM orders
        WHERE order_delivered_customer_date IS NOT NULL
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/late-deliveries")
def late_deliveries(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            COUNT(*) AS late_delivery_count
        FROM orders
        WHERE order_delivered_customer_date IS NOT NULL
          AND order_delivered_customer_date > order_estimated_delivery_date
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/top-customers")
def top_customers(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            c.customer_unique_id,
            SUM(oi.price) AS lifetime_value
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_unique_id
        ORDER BY lifetime_value DESC
        LIMIT 20
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/repeat-customers")
def repeat_customers(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            COUNT(*) AS repeat_customer_count
        FROM (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
            HAVING order_count > 1
        )
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/payment-methods")
def payment_methods(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            payment_type,
            COUNT(*) AS usage_count
        FROM payments
        GROUP BY payment_type
        ORDER BY usage_count DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)

@app.get("/analytics/cancellation-rate")
def cancellation_rate(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            (CAST(SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS FLOAT)
             / COUNT(*)) * 100 AS cancellation_rate_percent
        FROM orders
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dataframe_to_records(df)[0]

@app.get("/analytics/monthly-order-growth")
def monthly_order_growth(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            strftime('%Y-%m', order_purchase_timestamp) AS month,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY month
        ORDER BY month
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Calculate month-over-month growth % in Python, since SQLite
    # doesn't easily support "compare this row to the previous row"
    df["previous_month_orders"] = df["order_count"].shift(1)
    df["growth_percent"] = (
        (df["order_count"] - df["previous_month_orders"])
        / df["previous_month_orders"]
    ) * 100

    return dataframe_to_records(df)

@app.get("/analytics/yearly-revenue-growth")
def yearly_revenue_growth(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
        SELECT
            strftime('%Y', o.order_purchase_timestamp) AS year,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY year
        ORDER BY year
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["previous_year_revenue"] = df["total_revenue"].shift(1)
    df["growth_percent"] = (
        (df["total_revenue"] - df["previous_year_revenue"])
        / df["previous_year_revenue"]
    ) * 100

    return dataframe_to_records(df)

# ----------------------------------------------------
# Order Details (Nested JSON)
# ----------------------------------------------------
@app.get("/orders/{order_id}/details")
def order_details(
    order_id: str,
    x_api_key: str = Header(None)
):

    verify_key(x_api_key)

    conn = get_connection()

    order = pd.read_sql(
        "SELECT * FROM orders WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    if order.empty:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    items = pd.read_sql(
        "SELECT * FROM order_items WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    payments = pd.read_sql(
        "SELECT * FROM payments WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    reviews = pd.read_sql(
        "SELECT * FROM reviews WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    conn.close()

    return {
        "order": dataframe_to_records(order)[0],
        "items": dataframe_to_records(items),
        "payments": dataframe_to_records(payments),
        "reviews": dataframe_to_records(reviews)
    }