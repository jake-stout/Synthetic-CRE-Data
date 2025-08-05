import os
from typing import Optional

from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

engine = create_engine(DATABASE_URL)
app = FastAPI()


@app.get("/transactions")
def read_transactions(
    cash_account: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
):
    query = "SELECT txn_id, amount, date, entity, cash_account FROM streamed_transactions"
    conditions = []
    params = {}
    if cash_account:
        conditions.append("cash_account = :cash_account")
        params["cash_account"] = cash_account
    if start_date:
        conditions.append("date >= :start_date")
        params["start_date"] = start_date
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY date DESC LIMIT 100"

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(row) for row in result]
    return rows
