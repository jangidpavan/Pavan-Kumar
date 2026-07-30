import sqlite3
import pandas as pd
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "olist.db"
EXPORT_DIR = BASE_DIR / "powerbi_data"

# Create the export folder if it doesn't exist yet
EXPORT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

tables = [
    "customers",
    "orders",
    "order_items",
    "payments",
    "products",
    "sellers",
    "reviews",
    "geolocation",
    "category_translation",
]

for table in tables:
    print(f"Exporting {table}...")
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    df.to_csv(EXPORT_DIR / f"{table}.csv", index=False)

conn.close()

print("\n✅ All tables exported for Power BI!")
print(f"Files saved in: {EXPORT_DIR}")