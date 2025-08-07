import os
import pandas as pd
from sqlalchemy import create_engine

# Define connection parameters from environment variables with defaults
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "54322")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Create SQLAlchemy engine
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Base path to your CSVs
base_path = "data/raw/synthetic/simulated/yardi"

# List of tables to load
tables = [
    "tenants", "units", "leases", "payment_schedule", "vendors",
    "cust_invoices", "vend_invoices", "checkreg", "receipts", "gltran", "properties"
]

for table in tables:
    csv_path = os.path.join(base_path, f"{table}.csv")
    print(f"Loading: {table} from {csv_path}")
    df = pd.read_csv(csv_path)
    df.to_sql(table, con=engine, if_exists="replace", index=False)
    print(f"✓ Loaded {table} into database.")

print("All tables loaded into PostgreSQL.")
