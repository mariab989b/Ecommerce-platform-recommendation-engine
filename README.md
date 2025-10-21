# E-Commerce Platform with Real-Time Recommendation Engine

A production-ready e-commerce platform built with **Streamlit**, **Apache Kafka**, **PostgreSQL**, and **Redis**, featuring real-time product recommendations powered by event-driven architecture.

## 🏗️ Architecture
```
┌─────────────────┐
│   Streamlit     │ ← User Interface
│   (Frontend)    │
└────────┬────────┘
         │
         ↓ (Product Views)
┌─────────────────┐
│  Apache Kafka   │ ← Message Broker
│   (RedPanda)    │
└────────┬────────┘
         │
         ↓ (Events)
┌─────────────────┐
│   Consumer      │ ← Event Processing
│  (Python)       │
└────┬───────┬────┘
     │       │
     ↓       ↓
┌─────────┐ ┌─────────┐
│ Redis   │ │Postgres │
│(Reco)   │ │(Analytics)
└─────────┘ └─────────┘
```

## 🚀 Features

### Current Implementation
- **Product Catalog**: Browse 16+ products across multiple categories
- **Real-Time Events**: Track user interactions via Kafka
- **Recommendations**: The recommandation is simulated with a csv file
- **Session Management**: Guest and authenticated user support
- **Event Analytics**: Store and analyze product views in PostgreSQL
- **Caching Layer**: Redis for fast recommendation retrieval

### Technical Stack
- **Frontend**: Streamlit 1.37.0
- **Message Broker**: RedPanda (Kafka-compatible)
- **Database**: PostgreSQL 13
- **Cache**: Redis 7
- **Orchestration**: Kubernetes (Docker Desktop)
- **Monitoring**: Prometheus + Grafana
- **Language**: Python 3.11

## 📋 Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl configured
- Python 3.11+
- 8GB RAM minimum
- Ports available: 8501 (Streamlit), 9092 (Kafka), 5432 (PostgreSQL), 6379 (Redis)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ecommerce-platform-recommendation-engine.git
cd ecommerce-platform-recommendation-engine
```

### 2. Project Structure
```
.
├── App.py                      # Main Streamlit application
├── pages/
│   ├── 1_Catalog.py           # Product catalog page
│   ├── 2_Product_Detail.py    # Product details with recommendations
│   └── 3_Cart.py              # Shopping cart
├── lib/
│   ├── events.py              # Event dispatcher (Kafka producer)
│   ├── data_io.py             # Data utilities
│   └── auth.py                # Authentication utilities
├── src/
│   ├── consumer.py            # Kafka consumer with recommendation logic
│   └── producer.py            # Test event producer
├── data/
│   └── produit.csv            # Product catalog
├── assets/
│   └── images/                # Product images
├── k8s/                       # Kubernetes manifests
├── Dockerfile                 # Streamlit container
├── Dockerfile.consumer        # Consumer container
└── requirements.txt
```

### 3. Deploy Infrastructure
```bash
# Create namespace
kubectl create namespace ecommerce-platform

# Deploy services
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redpanda-deployment.yaml

# Wait for services to be ready
kubectl -n ecommerce-platform get pods -w
```

### 4. Initialize Database
```bash
# Create PostgreSQL tables
kubectl -n ecommerce-platform exec -it deploy/postgres -- psql -U admin -d ecommerce_analytics << 'SQL'
CREATE TABLE IF NOT EXISTS product_views (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(255),
    session_id VARCHAR(255),
    produit_id INTEGER,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_product_views_produit ON product_views(produit_id);
CREATE INDEX idx_product_views_session ON product_views(session_id);
SQL
```

### 5. Build Application Images
```bash
# Build Streamlit frontend
docker build -t streamlit-ecommerce:latest .

# Build Kafka consumer
docker build -f Dockerfile.consumer -t consumer-ecom:latest .
```

### 6. Create ConfigMap for Product Data
```bash
kubectl -n ecommerce-platform create configmap produit-csv \
  --from-file=produit.csv=data/produit.csv
```

### 7. Deploy Applications
```bash
# Deploy Streamlit
kubectl apply -f k8s/streamlit-deployment.yaml

# Deploy Consumer
kubectl apply -f k8s/consumer-deployment.yaml

# Verify deployments
kubectl -n ecommerce-platform get pods
```

### 8. Access the Application
```bash
# Port-forward Streamlit
kubectl -n ecommerce-platform port-forward svc/streamlit-service 8501:8501
```

Open your browser: **http://localhost:8501**

## 🎯 Usage

### User Flow

1. **Browse Catalog**: Navigate to "Product Catalog" in the sidebar
2. **Filter Products**: Use category filters and search
3. **View Details**: Click "View Details" on any product
4. **Get Recommendations**: See similar products based on your browsing
5. **Track Events**: All interactions are sent to Kafka in real-time

### Test Accounts
```
Email: alice@demo.com
Password: alice123

Email: bob@demo.com
Password: bob123
```

## 📊 Monitoring

### View Logs
```bash
# Streamlit logs
kubectl -n ecommerce-platform logs -f deploy/streamlit

# Consumer logs
kubectl -n ecommerce-platform logs -f deploy/consumer

# Kafka messages
kubectl -n ecommerce-platform exec -it redpanda-0 -- \
  rpk topic consume product_views
```

### Check Database
```bash
# Connect to PostgreSQL
kubectl -n ecommerce-platform exec -it deploy/postgres -- \
  psql -U admin -d ecommerce_analytics

# View product views
SELECT produit_id, COUNT(*) as views 
FROM product_views 
GROUP BY produit_id 
ORDER BY views DESC;
```

### Check Redis
```bash
# Connect to Redis
kubectl -n ecommerce-platform exec -it deploy/redis -- redis-cli

# View recommendations
KEYS recommendations:*
GET recommendations:1
```

### Grafana Dashboard
```bash
# Port-forward Grafana
kubectl -n ecommerce-platform port-forward svc/grafana-service 3000:3000
```

Access: **http://localhost:3000** (admin/admin)
