# lib/events.py
from __future__ import annotations
import os, time, json, uuid
from typing import Any, Dict, Optional
from kafka import KafkaProducer

def _json(v: Dict[str, Any]) -> bytes:
    return json.dumps(v, ensure_ascii=False).encode("utf-8")

class EventDispatcher:
    def __init__(self, backend: str, store, kafka_conf: Optional[dict] = None, retries: int = 3, backoff: float = 0.2):
        # backend ignoré (mode Kafka only pour v1)
        self.brokers = os.getenv("KAFKA_BROKERS", "redpanda-service:9092")
        self.topic_views = os.getenv("KAFKA_TOPIC_VIEWS", "product_views")
        self.topic_events = os.getenv("KAFKA_TOPIC_EVENTS", "events_app")
        self.retries = max(0, int(retries))
        self.backoff = max(0.0, float(backoff))
        self._producer = None

    def _ensure_producer(self):
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.brokers.split(","),
                value_serializer=lambda v: _json(v),
                key_serializer=lambda k: (k or "").encode("utf-8"),
                acks="all",
                linger_ms=50,
                retries=0,  # on gère nous-mêmes de petits retries
            )

    def emit_view(self, client_id: str, produit_id: int, session_id: str, timestamp: str):
        """Envoie un événement product_view à Kafka"""
        self._send(self.topic_views, client_id, {
            "client_id": client_id,
            "session_id": session_id,
            "produit_consulter_id": int(produit_id),
            "timestamp": timestamp,
        })

    def emit_event(self, client_id: Optional[str], session_id: str, event_type: str, payload: Dict[str, Any], timestamp: str):
        """Envoie un événement générique à Kafka"""
        self._send(self.topic_events, client_id or "anonymous", {
            "client_id": client_id or "anonymous",
            "session_id": session_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": timestamp,
        })

    def _send(self, topic: str, key: str, value: Dict[str, Any]):
        self._ensure_producer()
        attempts = self.retries + 1
        for i in range(attempts):
            try:
                self._producer.send(topic, key=key, value=value)
                # on peut laisser Kafka batcher ; si tu veux flush à chaque fois : self._producer.flush()
                return
            except Exception as e:
                # ne jamais bloquer l'UX : petits retries puis abandon silencieux
                if i < attempts - 1:
                    time.sleep(self.backoff)
                else:
                    # log minimal sur stdout (visible via kubectl logs)
                    print(f"[dispatcher] send failed topic={topic} key={key} err={e}", flush=True)
                    return