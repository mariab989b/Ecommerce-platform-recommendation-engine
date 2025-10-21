FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl gcc g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY App.py ./
COPY lib/ ./lib/
COPY pages/ ./pages/
COPY assets/images/ ./assets/images/

# Copier le CSV dans un emplacement temporaire
COPY data/produit.csv /tmp/produit.csv

# Script d'init
COPY init.sh /app/init.sh

RUN useradd -m streamlit && \
    chown -R streamlit:streamlit /app && \
    chmod +x /app/init.sh

USER streamlit

EXPOSE 8501

CMD ["/app/init.sh"]