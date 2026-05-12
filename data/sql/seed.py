"""
Generates shop.db — the SQLite database used by the SQL challenge.

Schema:
  categories  (id, name)
  products    (id, name, category_id, price)
  customers   (id, name, email, region, created_at)
  orders      (id, customer_id, ordered_at, status)
  order_items (id, order_id, product_id, quantity, unit_price)

Run with: python data/sql/seed.py
Creates:  data/sql/shop.db
"""

import sqlite3
import random
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

REGIONS = ["Nord", "Sud", "Est", "Ouest", "Centre"]
CATEGORIES = ["Électronique", "Vêtements", "Alimentation", "Maison", "Sport"]

PRODUCTS = [
    ("Smartphone X", 0, 699.99),
    ("Casque BT", 0, 89.99),
    ("Câble USB-C", 0, 12.99),
    ("Tablette Pro", 0, 449.99),
    ("T-shirt coton", 1, 19.99),
    ("Jean slim", 1, 49.99),
    ("Veste hiver", 1, 129.99),
    ("Café 1kg", 2, 14.99),
    ("Chocolat noir", 2, 3.49),
    ("Huile d'olive", 2, 8.99),
    ("Lampe bureau", 3, 39.99),
    ("Coussin déco", 3, 24.99),
    ("Vélo route", 4, 899.99),
    ("Tapis yoga", 4, 29.99),
    ("Gourde inox", 4, 22.99),
]

# Intentional data quality issues for C1/C2/C3
BAD_EMAILS = [
    "ALICE@EXAMPLE.COM",        # uppercase
    "  bob@example.com  ",      # leading/trailing spaces
    "charlie@@example.com",     # double @
    "diana@",                   # incomplete
    "valid@example.com",
]

random.seed(42)


def gen_customers(n=80):
    rows = []
    for i in range(1, n + 1):
        name = f"Client_{i:03d}"
        if i <= len(BAD_EMAILS):
            email = BAD_EMAILS[i - 1]
        else:
            email = f"client{i}@shop.fr"
        region = random.choice(REGIONS)
        # created_at spread across 2022-2024
        start = date(2022, 1, 1)
        created = start + timedelta(days=random.randint(0, 1095))
        rows.append((i, name, email, region, str(created)))
    return rows


def gen_orders(customers, n=400):
    rows = []
    for i in range(1, n + 1):
        cid = random.choice(customers)[0]
        # spread orders across 2023-2024
        start = date(2023, 1, 1)
        ordered = start + timedelta(days=random.randint(0, 729))
        status = random.choices(["completed", "cancelled", "pending"], weights=[75, 15, 10])[0]
        rows.append((i, cid, str(ordered), status))
    return rows


def gen_order_items(orders, products, n_items=900):
    rows = []
    oi_id = 1
    for order in orders:
        n = random.randint(1, 4)
        chosen = random.sample(products, min(n, len(products)))
        for prod in chosen:
            qty = random.randint(1, 5)
            # introduce one outlier amount for C2 (anomaly detection)
            price = prod[3] if oi_id != 42 else prod[3] * 50
            rows.append((oi_id, order[0], prod[0], qty, round(price, 2)))
            oi_id += 1
    return rows


def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE categories (
            id   INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE products (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            price       REAL NOT NULL
        );
        CREATE TABLE customers (
            id         INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            email      TEXT,
            region     TEXT,
            created_at TEXT
        );
        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            ordered_at  TEXT NOT NULL,
            status      TEXT NOT NULL
        );
        CREATE TABLE order_items (
            id         INTEGER PRIMARY KEY,
            order_id   INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity   INTEGER NOT NULL,
            unit_price REAL NOT NULL
        );
    """)

    cur.executemany("INSERT INTO categories VALUES (?,?)",
                    [(i + 1, name) for i, name in enumerate(CATEGORIES)])

    product_rows = [(i + 1, name, cat_id + 1, price)
                    for i, (name, cat_id, price) in enumerate(PRODUCTS)]
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", product_rows)

    customers = gen_customers()
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    orders = gen_orders(customers)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)

    order_items = gen_order_items(orders, product_rows)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", order_items)

    # Orphan order_items row for C3 (FK integrity check)
    cur.execute("INSERT INTO order_items VALUES (9999, 9999, 1, 1, 9.99)")

    # Duplicate customer for C3
    cur.execute("INSERT INTO customers VALUES (9998, 'Client_001', 'dup@shop.fr', 'Nord', '2023-01-01')")

    con.commit()
    con.close()
    print(f"shop.db created at {DB_PATH}")


if __name__ == "__main__":
    build()
