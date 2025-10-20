FROM python:3.11-slim

LABEL maintainer="maria@ecommerce.local"
LABEL description="Streamlit E-commerce Platform with Kafka Integration"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY App.py ./
COPY init_data.py ./
COPY lib/ ./lib/
COPY pages/ ./pages/

# Créer les répertoires
RUN mkdir -p /app/data /app/assets/images

# Copier les fichiers de données
COPY data/produit.csv /app/data/produit.csv

# Copier les images (avec gestion d'erreur bash)
RUN --mount=type=bind,source=assets/images,target=/tmp/images \
    if [ -d /tmp/images ] && [ "$(ls -A /tmp/images)" ]; then \
        cp -r /tmp/images/* /app/assets/images/ && echo "✅ Images copied"; \
    else \
        echo "⚠️ No images found, will use placeholders"; \
    fi

# Créer le fichier config.yaml
RUN printf "excel_path: /app/data/ecommerce.xlsx\nevents_backend: kafka\nkafka:\n  bootstrap_servers: redpanda-service:9092\n  topic_views: product_views\n  topic_events: events_app\n" > /app/config.yaml

# Vérifier que le CSV est bien là
RUN ls -la /app/data/produit.csv && echo "✅ CSV found" || (echo "❌ CSV NOT found" && exit 1)

# Initialiser la base de données
RUN python init_data.py

# Créer un utilisateur non-root
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

USER streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "App.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true"]