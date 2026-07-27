# Olist Interview API

## Overview

This project contains a REST API built using FastAPI and the Olist E-commerce dataset.

The purpose of this repository is to be used as a technical assessment for Data Analyst candidates.

---

## Dataset

The CSV datasets are available inside the `data/` folder.

---

## Installation

Clone the repository

```bash
git clone https://github.com/sambhatnagar4/olist-interview-api.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Load Database

Run

```bash
python scripts/load_data.py
```

This will create the SQLite database (`olist.db`).

---

## Start the API

```bash
uvicorn api.main:app --reload
```

---

## API Documentation

After starting the server, open

```
http://127.0.0.1:8000/docs
```

---

## Authentication

All endpoints require the API key:

```
candidate-test-2026
```

Pass it in the request header:

```
x-api-key: candidate-test-2026
```

---

## Available Endpoints

GET /

GET /customers

GET /orders

GET /order_items

GET /payments

GET /products

GET /sellers

GET /reviews

GET /geolocation

GET /category_translation

GET /orders/{order_id}/details

---

## Candidate Task

Candidates are expected to:

- Understand the existing project
- Work with SQLite
- Write SQL queries
- Extend the API with new endpoints
- Build analytical endpoints
- Follow clean coding practices
- Document their work

---

## Technologies Used

- Python
- FastAPI
- SQLite
- Pandas
