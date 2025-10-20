## seed_data.py

import os
import pandas as pd
from lib.data_io import ExcelStore, DEFAULT_SHEETS

EXCEL_PATH = 'data/ecommerce.xlsx'

PRODUCT_PLACEHOLDERS = [
    ("Wireless Mouse", "Accessories", 19.99, 50),
    ("Mechanical Keyboard", "Accessories", 59.99, 35),
    ("USB-C Hub", "Accessories", 29.99, 40),
    ("27\" Monitor", "Displays", 199.00, 20),
    ("Laptop Stand", "Accessories", 24.90, 60),
    ("Noise-canceling Headphones", "Audio", 129.00, 25),
    ("Webcam 1080p", "Video", 49.00, 30),
    ("Portable SSD 1TB", "Storage", 99.00, 22),
    ("Gaming Chair", "Furniture", 149.00, 12),
    ("Smart LED Strip", "Smart Home", 39.00, 45),
]

IMG = "https://picsum.photos/seed/{seed}/400/300"


def run_seed():
    store = ExcelStore(EXCEL_PATH)
    # Users (admin, 2 customers, bot)
    users = pd.DataFrame([
        {"id": 1, "email": "admin@demo.local", "password": "admin", "role": "admin"},
        {"id": 2, "email": "alice@demo.local", "password": "alice", "role": "customer"},
        {"id": 3, "email": "bob@demo.local", "password": "bob", "role": "customer"},
        {"id": 4, "email": "bot@demo.local", "password": "bot", "role": "customer"},
    ], columns=["id","email","password","role"])

    products = []
    pid = 1
    for i, (name, cat, price, stock) in enumerate(PRODUCT_PLACEHOLDERS, start=1):
        products.append({
            "id": pid,
            "name": name,
            "category": cat,
            "price": price,
            "currency": "EUR",
            "stock": stock,
            "image_url": IMG.format(seed=i),
            "active": True,
        })
        pid += 1

    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='w') as w:
        pd.DataFrame(users).to_excel(w, sheet_name='users', index=False)
        pd.DataFrame(products).to_excel(w, sheet_name='products', index=False)
        pd.DataFrame(columns=["id","user_id","created_at","total","status","payment_txn_id"]).to_excel(w, sheet_name='orders', index=False)
        pd.DataFrame(columns=["order_id","product_id","qty","unit_price"]).to_excel(w, sheet_name='order_items', index=False)
        pd.DataFrame(columns=["id","ts","user_id","type","payload_json"]).to_excel(w, sheet_name='events', index=False)

if __name__ == '__main__':
    run_seed()
    print(f"Seeded {EXCEL_PATH}")