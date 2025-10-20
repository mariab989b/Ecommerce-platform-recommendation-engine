# --- App.py (extrait à intégrer) ---
import os, json, time
import streamlit as st
import pandas as pd
import redis
from kafka import KafkaProducer

BOOTSTRAP   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda-service:9092")
TOPIC_VIEWS = os.getenv("KAFKA_TOPIC_VIEWS", "product_views")
REDIS_HOST  = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT  = int(os.getenv("REDIS_PORT", "6379"))

@st.cache_resource
def get_producer():
    return KafkaProducer(
        bootstrap_servers=[s.strip() for s in BOOTSTRAP.split(",") if s.strip()],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

@st.cache_resource
def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

producer = get_producer()
r = get_redis()

# Chargez votre CSV (adaptez le chemin)
df = pd.read_csv("data/produit.csv")

user_id = st.session_state.get("user_id", "anonymous")

st.header("Product Catalog")
for _, row in df.iterrows():
    pid = str(row["ID"])
    with st.container(border=True):
        st.image(row["Path_image"], use_container_width=True)  # images en assets (cf. Dockerfile)
        st.subheader(row["Product_Name"])
        st.caption(f"{row['Category']} • {row['Brand']} • {row['Price']} €")
        if st.button("Voir", key=f"view_{pid}"):
            # 1) envoyer l'évènement "view"
            evt = {"type": "view", "user_id": user_id, "product_id": pid, "ts": time.time()}
            producer.send(TOPIC_VIEWS, value=evt)
            producer.flush()

            # 2) lecture des recos en Redis: recs:{user_id}:{product_id} (backoff court)
            key = f"recs:{user_id}:{pid}"
            recs = None
            for _ in range(10):  # ~ 2 secondes
                val = r.get(key)
                if val:
                    recs = json.loads(val)
                    break
                time.sleep(0.2)

            st.markdown("### Recommandations")
            if recs:
                # si vous voulez montrer les images/titres:
                rid_set = set(str(x["product_id"]) for x in recs)
                df_rec = df[df["ID"].astype(str).isin(rid_set)]
                for _, rr in df_rec.iterrows():
                    st.write(f"• {rr['Product_Name']} — {rr['Price']} €")
            else:
                st.info("Aucune recommandation disponible pour le moment…")
