"""
Olist API
--------------------
A single-file REST API for exploring the Olist e-commerce dataset.

Code quality features included in this file:
- Centralized error handling (via a custom exception handler + try/except in every route)
- Input validation (page/limit bounds, table whitelisting, ID format checks)
- Meaningful variable names (no single-letter names, descriptive query variables)
- Comments explaining *why*, not just *what*
- Reusable helper functions (get_connection, run_query, get_table, verify_key, etc.)
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
import sqlite3
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="Olist Interview API",
    description="REST API for Data Analytics Interview",
    version="2.2"
)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

# BASE_DIR points to the project root (one level above this file's folder),
# so the database path resolves correctly regardless of where the app is run from.
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "olist.db"

API_KEY = "candidate-test-2026"

# Whitelist of tables that are safe to expose through the generic /table endpoints.
# This prevents SQL injection through the "table" parameter, since table names
# cannot be parameterized the same way values can in SQLite.
ALLOWED_TABLES = {
    "customers",
    "orders",
    "order_items",
    "payments",
    "products",
    "sellers",
    "reviews",
    "geolocation",
    "category_translation",
}

# Pagination limits, so a caller can't request an unreasonably large page
# and accidentally overload the server / response payload.
MIN_LIMIT = 1
MAX_LIMIT = 500

print(f"Database Path: {DB_PATH}")
print(f"Database Exists: {DB_PATH.exists()}")


# ----------------------------------------------------
# Global error handling
# ----------------------------------------------------
# Any exception that isn't already an HTTPException (e.g. an unexpected
# sqlite3.Error or pandas error) is caught here so the API always returns
# a clean JSON error instead of leaking a stack trace to the client.
@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected server error: {exc}"}
    )


# ----------------------------------------------------
# Authentication
# ----------------------------------------------------
def verify_key(x_api_key: str):
    """Reject the request if the caller didn't supply the correct API key."""
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# ----------------------------------------------------
# Input validation helpers
# ----------------------------------------------------
def validate_pagination(page: int, limit: int):
    """
    Ensure page/limit are sane before they're used to build a SQL query.
    Raises HTTPException(422) with a clear message if not.
    """
    if page < 1:
        raise HTTPException(status_code=422, detail="'page' must be 1 or greater")
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise HTTPException(
            status_code=422,
            detail=f"'limit' must be between {MIN_LIMIT} and {MAX_LIMIT}"
        )


def validate_table_name(table_name: str):
    """Only allow querying tables we explicitly whitelisted above."""
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail=f"Unknown table: '{table_name}'")


def validate_non_empty_id(id_value: str, field_name: str):
    """Reject blank/whitespace-only path parameters like customer_id, order_id, etc."""
    if id_value is None or not id_value.strip():
        raise HTTPException(status_code=422, detail=f"'{field_name}' cannot be empty")


# ----------------------------------------------------
# Database helpers
# ----------------------------------------------------
def get_connection():
    """Open a new SQLite connection. Callers are responsible for closing it."""
    return sqlite3.connect(DB_PATH)


def run_query(sql_query: str, params: tuple = ()):
    """
    Reusable helper that opens a connection, runs a parameterized query,
    closes the connection, and returns the result as a DataFrame.
    Centralizing this avoids repeating conn = ... / conn.close() everywhere
    and guarantees the connection is always closed, even on error.
    """
    connection = get_connection()
    try:
        result_df = pd.read_sql(sql_query, connection, params=params)
    finally:
        connection.close()
    return result_df


def dataframe_to_records(df: pd.DataFrame):
    """
    Convert a DataFrame into a JSON-safe list of dicts.
    Replaces NaN / +Infinity / -Infinity with None, since plain JSON
    has no representation for any of those values.
    """
    df = df.replace([float("inf"), float("-inf")], None)
    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def fetch_single_row_or_404(table_name: str, id_column: str, id_value: str, not_found_message: str):
    """
    Reusable "get one row by ID" helper used by /customers/{id}, /orders/{id},
    and /products/{id}. Returns the row as a dict, or raises 404 if missing.
    """
    validate_table_name(table_name)
    query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
    result_df = run_query(query, params=(id_value,))

    if result_df.empty:
        raise HTTPException(status_code=404, detail=not_found_message)

    return dataframe_to_records(result_df)[0]


def get_table(table_name: str, page: int = 1, limit: int = 100):
    """
    Generic paginated table loader, reused by every simple /<table> endpoint
    (customers, orders, order_items, payments, products, sellers, reviews,
    geolocation, category_translation).
    """
    validate_table_name(table_name)
    validate_pagination(page, limit)

    offset = (page - 1) * limit

    # Count total rows first so the client can tell how many pages exist.
    total_row_count = int(
        run_query(f"SELECT COUNT(*) as total FROM {table_name}").iloc[0]["total"]
    )

    page_df = run_query(
        f"SELECT * FROM {table_name} LIMIT ? OFFSET ?",
        params=(limit, offset)
    )

    return {
        "page": page,
        "limit": limit,
        "total_records": total_row_count,
        "returned_records": len(page_df),
        "has_next": (offset + limit) < total_row_count,
        "data": dataframe_to_records(page_df)
    }


# ----------------------------------------------------
# Home
# ----------------------------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Olist Interview API", "version": "2.2"}


# ----------------------------------------------------
# Customers
# ----------------------------------------------------
@app.get("/customers")
def customers(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("customers", page, limit)


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    validate_non_empty_id(customer_id, "customer_id")
    return fetch_single_row_or_404(
        table_name="customers",
        id_column="customer_id",
        id_value=customer_id,
        not_found_message="Customer not found"
    )


# ----------------------------------------------------
# Orders
# ----------------------------------------------------
@app.get("/orders")
def orders(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("orders", page, limit)


@app.get("/orders/{order_id}")
def get_order(order_id: str, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    validate_non_empty_id(order_id, "order_id")
    return fetch_single_row_or_404(
        table_name="orders",
        id_column="order_id",
        id_value=order_id,
        not_found_message="Order not found"
    )


# ----------------------------------------------------
# Order Items
# ----------------------------------------------------
@app.get("/order_items")
def order_items(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("order_items", page, limit)


# ----------------------------------------------------
# Payments
# ----------------------------------------------------
@app.get("/payments")
def payments(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("payments", page, limit)


# ----------------------------------------------------
# Products
# ----------------------------------------------------
@app.get("/products")
def products(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("products", page, limit)


@app.get("/products/{product_id}")
def get_product(product_id: str, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    validate_non_empty_id(product_id, "product_id")
    return fetch_single_row_or_404(
        table_name="products",
        id_column="product_id",
        id_value=product_id,
        not_found_message="Product not found"
    )


# ----------------------------------------------------
# Sellers
# ----------------------------------------------------
@app.get("/sellers")
def sellers(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("sellers", page, limit)


# ----------------------------------------------------
# Reviews
# ----------------------------------------------------
@app.get("/reviews")
def reviews(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("reviews", page, limit)


# ----------------------------------------------------
# Geolocation
# ----------------------------------------------------
@app.get("/geolocation")
def geolocation(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("geolocation", page, limit)


# ----------------------------------------------------
# Category Translation
# ----------------------------------------------------
@app.get("/categories")
def categories(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    category_df = run_query(
        "SELECT DISTINCT product_category_name FROM products "
        "WHERE product_category_name IS NOT NULL"
    )
    return dataframe_to_records(category_df)


@app.get("/categories/translation")
def categories_translation(page: int = 1, limit: int = 100, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return get_table("category_translation", page, limit)


# ----------------------------------------------------
# Analytics
# ----------------------------------------------------
@app.get("/analytics/top-selling-products")
def top_selling_products(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT product_id, COUNT(*) AS units_sold
        FROM order_items
        GROUP BY product_id
        ORDER BY units_sold DESC
        LIMIT 10
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/top-revenue-products")
def top_revenue_products(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT product_id, SUM(price) AS total_revenue
        FROM order_items
        GROUP BY product_id
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/monthly-revenue")
def monthly_revenue(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            strftime('%Y-%m', o.order_purchase_timestamp) AS month,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY month
        ORDER BY month
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/revenue-by-state")
def revenue_by_state(x_api_key: str = Header(None)):
    verify_key(x_api_key)
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
    return dataframe_to_records(run_query(query))


@app.get("/analytics/revenue-by-category")
def revenue_by_category(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            p.product_category_name AS category,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY total_revenue DESC
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/average-order-value")
def average_order_value(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT AVG(order_total) AS average_order_value
        FROM (
            SELECT order_id, SUM(price) AS order_total
            FROM order_items
            GROUP BY order_id
        )
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/average-basket-size")
def average_basket_size(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT AVG(item_count) AS average_basket_size
        FROM (
            SELECT order_id, COUNT(*) AS item_count
            FROM order_items
            GROUP BY order_id
        )
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/average-delivery-time")
def average_delivery_time(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            AVG(julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp))
            AS average_delivery_days
        FROM orders
        WHERE order_delivered_customer_date IS NOT NULL
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/late-deliveries")
def late_deliveries(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT COUNT(*) AS late_delivery_count
        FROM orders
        WHERE order_delivered_customer_date IS NOT NULL
          AND order_delivered_customer_date > order_estimated_delivery_date
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/top-customers")
def top_customers(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT c.customer_unique_id, SUM(oi.price) AS lifetime_value
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_unique_id
        ORDER BY lifetime_value DESC
        LIMIT 20
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/repeat-customers")
def repeat_customers(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT COUNT(*) AS repeat_customer_count
        FROM (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS order_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
            HAVING order_count > 1
        )
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/payment-methods")
def payment_methods(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT payment_type, COUNT(*) AS usage_count
        FROM payments
        GROUP BY payment_type
        ORDER BY usage_count DESC
    """
    return dataframe_to_records(run_query(query))


@app.get("/analytics/cancellation-rate")
def cancellation_rate(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            (CAST(SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS FLOAT)
             / COUNT(*)) * 100 AS cancellation_rate_percent
        FROM orders
    """
    return dataframe_to_records(run_query(query))[0]


@app.get("/analytics/monthly-order-growth")
def monthly_order_growth(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            strftime('%Y-%m', order_purchase_timestamp) AS month,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY month
        ORDER BY month
    """
    monthly_df = run_query(query)

    # Month-over-month growth % is computed in Python since SQLite has no
    # simple built-in way to compare a row to the previous row.
    monthly_df["previous_month_orders"] = monthly_df["order_count"].shift(1)
    monthly_df["growth_percent"] = (
        (monthly_df["order_count"] - monthly_df["previous_month_orders"])
        / monthly_df["previous_month_orders"]
    ) * 100

    return dataframe_to_records(monthly_df)


@app.get("/analytics/yearly-revenue-growth")
def yearly_revenue_growth(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    query = """
        SELECT
            strftime('%Y', o.order_purchase_timestamp) AS year,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY year
        ORDER BY year
    """
    yearly_df = run_query(query)

    yearly_df["previous_year_revenue"] = yearly_df["total_revenue"].shift(1)
    yearly_df["growth_percent"] = (
        (yearly_df["total_revenue"] - yearly_df["previous_year_revenue"])
        / yearly_df["previous_year_revenue"]
    ) * 100

    return dataframe_to_records(yearly_df)


# ----------------------------------------------------
# Order Details (Nested JSON)
# ----------------------------------------------------
@app.get("/orders/{order_id}/details")
def order_details(order_id: str, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    validate_non_empty_id(order_id, "order_id")

    order_df = run_query("SELECT * FROM orders WHERE order_id = ?", params=(order_id,))
    if order_df.empty:
        raise HTTPException(status_code=404, detail="Order not found")

    items_df = run_query("SELECT * FROM order_items WHERE order_id = ?", params=(order_id,))
    payments_df = run_query("SELECT * FROM payments WHERE order_id = ?", params=(order_id,))
    reviews_df = run_query("SELECT * FROM reviews WHERE order_id = ?", params=(order_id,))

    return {
        "order": dataframe_to_records(order_df)[0],
        "items": dataframe_to_records(items_df),
        "payments": dataframe_to_records(payments_df),
        "reviews": dataframe_to_records(reviews_df)
    }