CREATE TABLE cash_txn_source (
    txn_id STRING,
    amount DOUBLE,
    date TIMESTAMP(3),
    entity STRING,
    cash_account STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'cash_txn',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-group',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
);

CREATE TABLE streamed_transactions (
    txn_id STRING,
    amount DOUBLE,
    date TIMESTAMP(3),
    entity STRING,
    cash_account STRING
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://cre-db:5432/postgres',
    'table-name' = 'streamed_transactions',
    'driver' = 'org.postgresql.Driver',
    'username' = 'postgres',
    'password' = 'postgres'
);

INSERT INTO streamed_transactions
SELECT txn_id, amount, date, entity, cash_account
FROM cash_txn_source;
