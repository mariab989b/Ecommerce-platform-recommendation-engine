import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from pathlib import Path

st.set_page_config(page_title="Catalog", layout="wide")

st.markdown("""
<style>
    .product-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

if 'products' not in st.session_state:
    st.error("Please return to home page")
    st.stop()

def load_image(image_path):
    if image_path and Path(image_path).exists():
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    return None

st.title("Product Catalog")

if st.session_state.user:
    st.caption(f"Signed in as: {st.session_state.user['email']}")
else:
    st.caption(f"Session: {st.session_state.user_id[:15]}...")

st.markdown("---")

products = st.session_state.products
active = products[products['active'] == True].copy()

# Filters
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    cats = ['All'] + sorted(active['category'].unique().tolist())
    cat = st.selectbox("Category", cats)

with col2:
    search = st.text_input("Search", "")

with col3:
    sort = st.selectbox("Sort", ["Name", "Price: Low to High", "Price: High to Low"])

filtered = active.copy()

if cat != 'All':
    filtered = filtered[filtered['category'] == cat]

if search:
    filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

if sort == "Price: Low to High":
    filtered = filtered.sort_values('price')
elif sort == "Price: High to Low":
    filtered = filtered.sort_values('price', ascending=False)
else:
    filtered = filtered.sort_values('name')

st.success(f"{len(filtered)} products found")
st.markdown("---")

if len(filtered) == 0:
    st.warning("No products match your criteria")
else:
    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(filtered):
                product = filtered.iloc[idx]
                
                with col:
                    img = load_image(product['image_url'])
                    if img:
                        st.markdown(f'<img src="data:image/png;base64,{img}" style="width:100%; border-radius:8px;"/>', unsafe_allow_html=True)
                    else:
                        st.image("https://via.placeholder.com/400x300", use_container_width=True)
                    
                    st.subheader(product['name'])
                    st.write(f"**{product['price']:.2f} EUR**")
                    st.caption(f"{product['category']} • Stock: {product['stock']}")
                    
                    if st.button("View Details", key=f"view_{product['id']}", use_container_width=True):
                        try:
                            st.session_state.events.emit_view(
                                client_id=st.session_state.user_id,
                                produit_id=int(product['id']),
                                session_id=st.session_state.session_id,
                                timestamp=datetime.utcnow().isoformat()
                            )
                        except:
                            pass
                        
                        st.session_state.selected_product_id = int(product['id'])
                        st.switch_page("pages/2_Product_Detail.py")
                    
                    st.markdown("---")