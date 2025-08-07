# Synthetic CRE Data

Utilities for generating synthetic commercial real estate (CRE) data, loading it into PostgreSQL, and running simple streaming jobs with Apache Flink. These scripts are useful for demos or analytics testing.

## Prerequisites

Install the required Python packages:

```bash
pip install -r requirements.txt
```

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

### Run PostgreSQL, Kafka, and Flink with Docker

The repository includes a `docker-compose.yml` that starts PostgreSQL, Kafka, and a Flink cluster for local testing:

```bash
docker compose up -d
```

Use the make targets in `flink_jobs/Makefile` to submit the streaming jobs:

```bash
cd flink_jobs
make job        # start the ingestion job
make aggregation_job
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
