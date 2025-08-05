import json
import os
import random
import time
import uuid

from faker import Faker
from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "cash_txn")


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def generate_transaction(fake: Faker) -> dict:
    return {
        "txn_id": str(uuid.uuid4()),
        "amount": round(random.uniform(10.0, 10000.0), 2),
        "date": fake.iso8601(),
        "entity": fake.company(),
        "cash_account": fake.iban(),
    }


def main() -> None:
    fake = Faker()
    producer = create_producer()
    while True:
        message = generate_transaction(fake)
        producer.send(KAFKA_TOPIC, message)
        producer.flush()
        time.sleep(1)


if __name__ == "__main__":
    main()
