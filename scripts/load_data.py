import pandas as pd
import sqlite3
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "olist.db"

files = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# Explicit schema: types + primary/foreign keys
SCHEMA = {
    "customers": """
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_unique_id TEXT NOT NULL,
            customer_zip_code_prefix INTEGER,
            customer_city TEXT,
            customer_state TEXT
        )
    """,
    "sellers": """
        CREATE TABLE sellers (
            seller_id TEXT PRIMARY KEY,
            seller_zip_code_prefix INTEGER,
            seller_city TEXT,
            seller_state TEXT
        )
    """,
    "category_translation": """
        CREATE TABLE category_translation (
            product_category_name TEXT PRIMARY KEY,
            product_category_name_english TEXT
        )
    """,
    "products": """
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_category_name TEXT,
            product_name_lenght REAL,
            product_description_lenght REAL,
            product_photos_qty REAL,
            product_weight_g REAL,
            product_length_cm REAL,
            product_height_cm REAL,
            product_width_cm REAL,
            FOREIGN KEY (product_category_name) REFERENCES category_translation(product_category_name)
        )
    """,
    "orders": """
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_status TEXT,
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """,
    "order_items": """
        CREATE TABLE order_items (
            order_id TEXT NOT NULL,
            order_item_id INTEGER NOT NULL,
            product_id TEXT,
            seller_id TEXT,
            shipping_limit_date TIMESTAMP,
            price REAL,
            freight_value REAL,
            PRIMARY KEY (order_id, order_item_id),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
        )
    """,
    "payments": """
        CREATE TABLE payments (
            order_id TEXT NOT NULL,
            payment_sequential INTEGER NOT NULL,
            payment_type TEXT,
            payment_installments INTEGER,
            payment_value REAL,
            PRIMARY KEY (order_id, payment_sequential),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """,
    "reviews": """
        CREATE TABLE reviews (
            review_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            review_score INTEGER,
            review_comment_title TEXT,
            review_comment_message TEXT,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP,
            PRIMARY KEY (review_id, order_id),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """,
    "geolocation": """
        CREATE TABLE geolocation (
            geolocation_zip_code_prefix INTEGER,
            geolocation_lat REAL,
            geolocation_lng REAL,
            geolocation_city TEXT,
            geolocation_state TEXT
        )
    """,
}

# Load order matters: parents before children (FK dependencies)
LOAD_ORDER = [
    "category_translation",
    "customers",
    "sellers",
    "products",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "geolocation",
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
# cur.execute("PRAGMA foreign_keys = ON;")
for table in LOAD_ORDER:
    filename = files[table]
    csv_path = DATA_DIR / filename
    print(f"Loading {filename} into '{table}'...")

    # Drop table if it already exists, then create fresh with schema
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute(SCHEMA[table])

    df = pd.read_csv(csv_path)

    # Parse timestamp columns so they're stored consistently
    for col in df.columns:
        if "date" in col or "timestamp" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df.to_sql(table, conn, if_exists="append", index=False)

# ----------------------------------------------------
# Indexes — speed up joins and filtering on large tables
# ----------------------------------------------------

print("Creating indexes...")

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)",
    "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id)",
    "CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON reviews(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_products_category ON products(product_category_name)",
    "CREATE INDEX IF NOT EXISTS idx_customers_state ON customers(customer_state)",
    "CREATE INDEX IF NOT EXISTS idx_orders_purchase_ts ON orders(order_purchase_timestamp)",
]

for index_sql in indexes:
    cur.execute(index_sql)

print("Indexes created.")

conn.commit()
conn.close()

print("\n✅ Database created successfully with types, PKs, and FKs!")
print(f"Database saved at: {DB_PATH}")