import pandas as pd
import sqlite3
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "olist.db"

# Mapping of table names to CSV files
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

conn = sqlite3.connect(DB_PATH)

for table, filename in files.items():
    csv_path = DATA_DIR / filename
    print(f"Loading {filename}...")
    df = pd.read_csv(csv_path)
    df.to_sql(table, conn, if_exists="replace", index=False)

conn.close()

print("\n✅ Database created successfully!")
print(f"Database saved at: {DB_PATH}")