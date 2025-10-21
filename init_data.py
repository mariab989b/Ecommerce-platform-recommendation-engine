import pandas as pd
import os
from pathlib import Path
from lib.data_io import ExcelStore

EXCEL_PATH = 'data/ecommerce.xlsx'
CSV_PATH = 'data/produit.csv'

def init_database():
    print("="*60)
    print("🚀 INITIALISATION DE LA BASE DE DONNÉES")
    print("="*60)
    
    # Vérifier que le CSV existe
    if not os.path.exists(CSV_PATH):
        print(f"❌ Fichier {CSV_PATH} non trouvé")
        return
    
    # Lire le CSV
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV lu: {len(df)} produits")
    
    # Créer le store
    store = ExcelStore(EXCEL_PATH)
    
    # Convertir les produits en utilisant Path_image du CSV
    products = []
    for idx, row in df.iterrows():
        # Utiliser le chemin d'image du CSV
        image_path = str(row['Path_image']) if pd.notna(row['Path_image']) else ''
        
        product = {
            'id': int(row['ID']),
            'name': str(row['Product_Name']),
            'category': str(row['Category']),
            'price': float(row['Price']),
            'currency': 'EUR',
            'stock': int(row['Stock_Quantity']),
            'image_url': image_path,  # Chemin local
            'image_path': image_path,  # Pour référence
            'active': True
        }
        products.append(product)
    
    products_df = pd.DataFrame(products)
    store.write('products', products_df)
    print(f"✅ {len(products_df)} produits écrits")
    
    # Créer les utilisateurs
    users = pd.DataFrame([
        {"id": 1, "email": "admin@buyme.com", "password": "admin123", "role": "admin"},
        {"id": 2, "email": "alice@demo.com", "password": "alice123", "role": "customer"},
        {"id": 3, "email": "bob@demo.com", "password": "bob123", "role": "customer"},
    ])
    store.write('users', users)
    print(f"✅ {len(users)} utilisateurs créés")
    
    # Résumé
    print("\n📊 RÉSUMÉ:")
    print(f"   Produits: {len(products_df)}")
    print(f"   Catégories: {products_df['category'].nunique()}")
    for cat, count in products_df['category'].value_counts().items():
        print(f"      • {cat}: {count}")
    print(f"   Prix moyen: {products_df['price'].mean():.2f} EUR")
    print("="*60)

if __name__ == '__main__':
    init_database()
