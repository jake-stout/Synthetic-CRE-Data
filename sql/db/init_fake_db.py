import sqlite3
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'synthetic', 'simulated', 'yardi')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'fake_cashsight.db')

TABLES = [
    'tenants', 'units', 'leases', 'payment_schedule', 'vendors',
    'cust_invoices', 'vend_invoices', 'checkreg', 'receipts', 'gltran', 'properties'
]

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        for table in TABLES:
            csv_path = os.path.join(DATA_DIR, f"{table}.csv")
            if not os.path.exists(csv_path):
                print(f"Warning: {csv_path} not found, skipping {table}.")
                continue
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, if_exists='replace', index=False)
        print(f"Database created at {DB_PATH}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
