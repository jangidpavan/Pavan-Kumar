# Olist E-Commerce Analytics

A FastAPI-based analytics project built using the Olist Brazilian E-Commerce dataset. The project includes a SQLite database, REST APIs, SQL analytics, and a Power BI dashboard.

## Project Structure

```text
project-root/
├── api
│   ├── _pycache_
│   │   └── main.cpython-311.pyc
│   └── main.py
├── data
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
├── olist.db
├── powerbi_data
│   ├── category_translation.csv
│   ├── customers.csv
│   ├── geolocation.csv
│   ├── order_items.csv
│   ├── orders.csv
│   ├── payments.csv
│   ├── products.csv
│   ├── reviews.csv
│   └── sellers.csv
├── requirements.txt
└── scripts
    ├── export_for_powerbi.py
    └── load_data.py
├── CANDIDATE_TASK.md
├── Power-BI-Dashboard
│   ├── Power-BI-dashboard-1.png
│   ├── Power-BI-dashboard-2.png
│   └── olist_dashboard.pbix
├── README.md
├── SUBMISSION_GUIDELINES.md
```

## Setup

### Prerequisites

- Install **Python 3.11** or later.
- Verify the installation:

```bash
python3.11 --version
```

### Installation

1. Clone the repository. - https://github.com/jangidpavan/Pavan-Kumar.git

2. Create a virtual environment.

```bash
python3.11 -m venv .venv
```

3. Activate the virtual environment.

```bash
source .venv/bin/activate
```

> **Windows**
>
> ```bash
> .venv\Scripts\activate
> ```

4. Install the required dependencies.

```bash
pip install -r requirements.txt
```

5. Download the Olist dataset from Kaggle and place all CSV files inside the `data/` directory.

6. Create the SQLite database.

```bash
python scripts/load_data.py
```

7. Run the FastAPI application.

```bash
uvicorn api.main:app --reload
```

API Documentation:

```
http://127.0.0.1:8000/docs
```

8. Export data for Power BI (optional).

```bash
python scripts/export_for_powerbi.py
```

## Authentication

All endpoints except `/` require the following header:

```
X-API-Key: candidate-test-2026
```

## API Endpoints

### Resources

- `/customers`
- `/orders`
- `/order_items`
- `/payments`
- `/products`
- `/sellers`
- `/reviews`
- `/geolocation`
- `/categories`
- `/categories/translation`

### Analytics

- Top Selling Products
- Top Revenue Products
- Monthly Revenue
- Revenue by State
- Revenue by Category
- Average Order Value
- Average Basket Size
- Average Delivery Time
- Late Deliveries
- Top Customers
- Repeat Customers
- Payment Methods
- Cancellation Rate
- Monthly Order Growth
- Yearly Revenue Growth

## Dashboard

The Power BI dashboard includes:

- Revenue KPIs
- Monthly Revenue Trend
- Revenue by State
- Revenue by Category
- Payment Analysis
- Top Products
- Top Customers
- Delivery Performance

Power BI Dashboard
The Power BI dashboard screenshots are available in the Power-BI-Dashboard/ folder.
The Power BI report file is available as olist_dashboard.pbix in the same folder.

## Tech Stack

- FastAPI
- SQLite
- Pandas
- Power BI

## Notes

- Uses the Olist Brazilian E-Commerce dataset.
- Revenue is calculated from `order_items.price`.
- SQLite is used for simplicity and local development.