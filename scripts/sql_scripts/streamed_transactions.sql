CREATE TABLE IF NOT EXISTS streamed_transactions (
    txn_id TEXT PRIMARY KEY,
    amount NUMERIC,
    date TIMESTAMP,
    entity TEXT,
    cash_account TEXT
);
