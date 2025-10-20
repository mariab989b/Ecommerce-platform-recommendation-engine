import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Classe de configuration centralisée pour l'application ecommerce-platform."""

    # Kafka
    kafka_bootstrap: str
    kafka_topic: str

    # PostgreSQL
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Redis
    redis_host: str
    redis_port: int

    # Chemin du CSV des produits
    product_csv_path: str

    @classmethod
    def load(cls):
        """Charge la configuration depuis les variables d'environnement injectées par Kubernetes."""
        return cls(
            KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "redpanda-service:9092"),
            KAFKA_TOPIC_VIEWS = os.getenv("KAFKA_TOPIC_VIEWS", "product_views"),
            KAFKA_TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "events_app"),

            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", 5432)),
            postgres_db=os.getenv("POSTGRES_DB", "ecommerce_analytics"),
            postgres_user=os.getenv("POSTGRES_USER", "admin"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", "strongpassword123"),

            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", 6379)),

            product_csv_path=os.getenv("PRODUCT_CSV_PATH", "/app/data/produit.csv"),
        )
