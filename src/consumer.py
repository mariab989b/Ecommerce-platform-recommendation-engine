import os, json, redis
from kafka import KafkaConsumer
from collections import defaultdict, Counter

BROKERS = os.getenv("KAFKA_BROKERS", "redpanda-service:9092")
TOPIC_VIEWS = os.getenv("KAFKA_TOPIC_VIEWS", "product_views")
TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "events_app")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "ecom-consumer")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connexion Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Structure pour tracker les co-occurrences
product_views = defaultdict(list)  # session_id -> [product_ids]

def calculate_recommendations(product_id, top_n=3):
    """Calcule les produits souvent vus ensemble"""
    # Récupérer les sessions qui ont vu ce produit
    recommendations = Counter()
    
    for session_id, viewed_products in product_views.items():
        if product_id in viewed_products:
            # Compter les autres produits vus dans cette session
            for other_product in viewed_products:
                if other_product != product_id:
                    recommendations[other_product] += 1
    
    # Retourner les top N produits
    return [prod_id for prod_id, count in recommendations.most_common(top_n)]

def store_recommendations(product_id, recommended_ids):
    """Stocke les recommandations dans Redis"""
    key = f"recommendations:{product_id}"
    redis_client.setex(key, 3600, json.dumps(recommended_ids))  # Expire après 1h
    print(f"[REDIS] Stored recommendations for product {product_id}: {recommended_ids}")

def main():
    consumer = KafkaConsumer(
        TOPIC_VIEWS, TOPIC_EVENTS,
        bootstrap_servers=BROKERS.split(","),
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        key_deserializer=lambda b: b.decode("utf-8") if b else None,
    )

    print(f"[consumer] 🚀 Started listening on {BROKERS}")
    print(f"[consumer] 📡 Topics: [{TOPIC_VIEWS}, {TOPIC_EVENTS}]")
    print(f"[consumer] 👥 Group: {GROUP_ID}")
    print(f"[consumer] 📦 Redis: {REDIS_HOST}:{REDIS_PORT}")
    
    for msg in consumer:
        topic = msg.topic
        key = msg.key
        value = msg.value
        
        # Log
        print(f"[{topic}] key={key} value={value}", flush=True)
        
        # Si c'est un product_view
        if topic == TOPIC_VIEWS and 'produit_consulter_id' in value:
            session_id = value.get('session_id')
            product_id = value.get('produit_consulter_id')
            
            # Ajouter à l'historique de la session
            if product_id not in product_views[session_id]:
                product_views[session_id].append(product_id)
            
            # Calculer les recommandations
            recommendations = calculate_recommendations(product_id)
            
            # Stocker dans Redis
            if recommendations:
                store_recommendations(product_id, recommendations)
                print(f"[RECO] Product {product_id} -> Recommended: {recommendations}")

if __name__ == "__main__":
    main()
