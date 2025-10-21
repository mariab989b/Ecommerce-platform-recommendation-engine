#!/bin/bash
# Copier le CSV si absent
if [ ! -f /app/data/produit.csv ]; then
    echo "Copying CSV to mounted volume..."
    cp /tmp/produit.csv /app/data/produit.csv 2>/dev/null || echo "CSV already in place"
fi
exec streamlit run App.py --server.port=8501 --server.address=0.0.0.0
