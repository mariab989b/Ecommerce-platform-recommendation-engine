# consumer.py
import os, json, time, logging
from typing import List, Dict
from kafka import KafkaConsumer
import redis

logging.basicConfig(level=logging.INFO, format="[consumer] %(message)s")
log = logging.getLogger("consumer")

BROKERS      = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda-service:9092")
TOPIC_VIEWS  = os.getenv("KAFKA_TOPIC_VIEWS", "product_views")
GROUP_ID     = os.getenv("KAFKA_GROUP_ID", "ecom-consumer")
REDIS_HOST   = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT   = int(os.getenv("REDIS_PORT", "6379"))
REDIS_TTL_S  = int(os.getenv("RECS_TTL_SECONDS", "300"))

# Client Redis (UTF-8)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def compute_recommendations(user_id: str, product_id: str, top_n: int = 5) -> List[Dict]:
    """
    Baseline *exemple* : retourne N produits 'recommandés'.
    Remplacez par votre logique (cooccurrences, CF, contenu, embeddings, etc.)
    """
    # >>> À remplacer par vos scores/calculs :
    dummy = [{"product_id": "1", "score": 100},
             {"product_id": "2", "score": 90},
             {"product_id": "3", "score": 80},
             {"product_id": "4", "score": 70},
             {"product_id": "5", "score": 60}]
    # Éviter de recommander le produit en cours
    return [x for x in dummy if str(x["product_id"]) != str(product_id)][:top_n]

def write_recs_to_redis(user_id: str, product_id: str, recs: List[Dict], ttl=REDIS_TTL_S):
    key = f"recs:{user_id}:{product_id}"
    # Doc officielle : SET avec option EX (TTL en secondes)
    r.set(key, json.dumps(recs), ex=ttl)

def main():
    log.info(f"connecting Kafka @ {BROKERS}, topic={TOPIC_VIEWS}, group={GROUP_ID}")
    consumer = KafkaConsumer(
        TOPIC_VIEWS,
        bootstrap_servers=[s.strip() for s in BROKERS.split(",") if s.strip()],
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        key_deserializer=lambda b: b.decode("utf-8") if b else None,
    )

    for msg in consumer:
        evt = msg.value  # attendu: {"type":"view","user_id":"...","product_id":"...","ts":...}
        user_id = str(evt.get("user_id", "anonymous"))
        product_id = str(evt.get("product_i
