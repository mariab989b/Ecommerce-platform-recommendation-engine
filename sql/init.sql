-- Créer les tables
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2),
    category VARCHAR(100),
    brand VARCHAR(100),
    stock_quantity INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_views (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100)
);

CREATE INDEX idx_product_views_client ON product_views(client_id);
CREATE INDEX idx_product_views_product ON product_views(product_id);
CREATE INDEX idx_product_views_timestamp ON product_views(timestamp);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    viewed_product_id INTEGER NOT NULL,
    recommended_product_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conversion BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recommendations_client ON recommendations(client_id);
CREATE INDEX idx_recommendations_timestamp ON recommendations(timestamp);