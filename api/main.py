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
    df = df.where(pd.notnull(df), None)
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

@app.get("/category_translation")
def category_translation(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("category_translation", page, limit)


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