# CashSight

CashSight provides tools for generating synthetic property management data and loading it into a local PostgreSQL instance. It can be useful for demos or analytics testing.

## Prerequisites

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Key packages include `pandas`, `openpyxl`, `faker`, `sqlalchemy`, `psycopg2-binary` and `python-dotenv`.

## Usage

### Generate sample data

Run the data generation script to create CSV files under `data/raw/synthetic/simulated/yardi`.

```bash
python scripts/create_synthetic_sample_data.py
```

### Load data into PostgreSQL

Update the connection parameters at the top of `load_to_postgres.py` to match your environment and execute:

```bash
python scripts/load_to_postgres.py
```

This reads the generated CSVs and loads them into the specified database.

### Create a fake SQLite database

If you just want a lightweight demo database, run:

```bash
python cashsight/db/init_fake_db.py
```

This will create `data/fake_cashsight.db` populated with the sample CSV data.

### Run Postgres with Docker

To spin up a local PostgreSQL instance and pgAdmin using Docker Compose, first
update the connection settings in `.env` if needed. Then start the services:

```bash
docker compose up -d
```

Stop the containers when you are done:

```bash
docker compose down
```

### Run tests

Use `pytest` to run the unit tests:

```bash
pytest
```
