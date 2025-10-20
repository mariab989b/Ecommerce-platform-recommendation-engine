import pandas as pd
import os
from pathlib import Path
from lib.data_io import ExcelStore

EXCEL_PATH = 'data/ecommerce.xlsx'
CSV_PATH = 'data/produit.csv'  # Votre fichier CSV existant

def get_image_url(product_id, product_name, category):
    """Génère une URL d'image basée sur les infos du produit"""
    # Utiliser picsum avec seed pour avoir des images cohérentes
    seed = f"{category.lower()}_{product_id}"
    return f"https://picsum.photos/seed/{seed}/400/300"

def load_products_from_csv():
    """Charge les produits depuis le CSV"""
    if not os.path.exists(CSV_PATH):
        print(f"⚠️ Fichier {CSV_PATH} non trouvé")
        return None
    
    # Lire le CSV
    df = pd.read_csv(CSV_PATH)
    print(f"📦 {len(df)} produits trouvés dans {CSV_PATH}")
    
    # Mapper les colonnes du CSV vers le schéma attendu
    products = []
    for idx, row in df.iterrows():
        product = {
            'id': int(row['ID']),
            'name': str(row['Product_Name']),
            'category': str(row['Category']),
            'price': float(row['Price']),
            'currency': 'EUR',
            'stock': int(row['Stock_Quantity']),
            'image_url': get_image_url(row['ID'], row['Product_Name'], row['Category']),
            'image_path': '',  # Pas d'images locales pour l'instant
            'active': True
        }
        products.append(product)
    
    return pd.DataFrame(products)

def load_existing_excel():
    """Charge les données existantes du fichier Excel"""
    if os.path.exists(EXCEL_PATH):
        try:
            existing = pd.read_excel(EXCEL_PATH, sheet_name='products')
            print(f"📁 {len(existing)} produits trouvés dans Excel existant")
            return existing
        except Exception as e:
            print(f"⚠️ Erreur lecture Excel: {e}")
            return None
    return None

def init_database():
    store = ExcelStore(EXCEL_PATH)
    
    # Charger les produits depuis le CSV
    products_from_csv = load_products_from_csv()
    
    if products_from_csv is None or products_from_csv.empty:
        print("❌ Impossible de charger les produits depuis le CSV")
        return
    
    # Charger les données existantes
    existing_products = load_existing_excel()
    
    # Fusionner intelligemment
    if existing_products is not None and not existing_products.empty:
        # Garder les produits existants qui ne sont pas dans le CSV
        existing_ids = set(products_from_csv['id'].tolist())
        kept_products = existing_products[~existing_products['id'].isin(existing_ids)]
        
        if not kept_products.empty:
            print(f"✅ Conservation de {len(kept_products)} produits existants non présents dans le CSV")
            final_products = pd.concat([products_from_csv, kept_products], ignore_index=True)
        else:
            final_products = products_from_csv
    else:
        final_products = products_from_csv
    
    # Écrire les produits
    store.write('products', final_products)
    print(f"✅ {len(final_products)} produits écrits dans la base")
    
    # Créer les utilisateurs
    users = pd.DataFrame([
        {"id": 1, "email": "admin@buyme.com", "password": "admin123", "role": "admin"},
        {"id": 2, "email": "alice@demo.com", "password": "alice123", "role": "customer"},
        {"id": 3, "email": "bob@demo.com", "password": "bob123", "role": "customer"},
    ])
    
    try:
        existing_users = pd.read_excel(EXCEL_PATH, sheet_name='users')
        print(f"✅ {len(existing_users)} utilisateurs existants conservés")
    except:
        store.write('users', users)
        print(f"✅ {len(users)} utilisateurs créés")
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA BASE DE DONNÉES")
    print("="*60)
    print(f"✅ Produits actifs: {len(final_products[final_products['active'] == True])}")
    print(f"✅ Catégories: {final_products['category'].nunique()}")
    categories = final_products['category'].value_counts()
    for cat, count in categories.items():
        print(f"   - {cat}: {count} produits")
    print(f"✅ Stock total: {final_products['stock'].sum()} unités")
    print(f"✅ Prix moyen: {final_products['price'].mean():.2f} EUR")
    
    print("\n🛍️ Exemples de produits:")
    for _, product in final_products.head(5).iterrows():
        print(f"   • {product['name']}: {product['price']:.2f}€ (Stock: {product['stock']})")
    print("="*60)

if __name__ == '__main__':
    init_database()
