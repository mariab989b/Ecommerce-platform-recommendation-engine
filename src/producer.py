import os, json, time, uuid, random
from datetime import datetime, timezone
from kafka import KafkaProducer

BROKERS = os.getenv("KAFKA_BROKERS", "redpanda-service:9092")
TOPIC_VIEWS = os.getenv("KAFKA_TOPIC_VIEWS", "product_views")

def ts_iso():
    return datetime.now(timezone.utc).isoformat()

def new_session_id():
    return str(uuid.uuid4())

def main():
    producer = KafkaProducer(
        bootstrap_servers=BROKERS.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: (k or "").encode("utf-8"),
        acks="all",
        linger_ms=100,
        retries=3,
    )
    session_id = new_session_id()
    client_id = os.getenv("CLIENT_ID", "producer-simulator")

    # boucle simple
    while True:
        produit_id = random.randint(1, 50)  # adapte selon ton catalogue
        msg = {
            "client_id": client_id,
            "session_id": session_id,
            "produit_consulter_id": produit_id,
            "timestamp": ts_iso(),
        }
        # clé de partition = client_id
        producer.send(TOPIC_VIEWS, key=client_id, value=msg)
        producer.flush()
        time.sleep(2)  # ~30 vues/min ; ajuste si tu veux

if __name__ == "__main__":
    main()