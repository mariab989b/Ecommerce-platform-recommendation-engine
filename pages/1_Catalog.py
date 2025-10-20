import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Product Catalog", page_icon="📦", layout="wide")

# Check if store is initialized
if 'store' not in st.session_state:
    st.error("Please go to Home page first to initialize the app")
    st.stop()

# Show user status
if st.session_state.user:
    st.caption(f"👤 Shopping as: **{st.session_state.user['email']}**")
else:
    st.caption(f"🔓 Browsing as Guest (ID: {st.session_state.user_id[:20]}...)")

st.title("📦 Product Catalog")

# Load products
products = st.session_state.store.read('products')
active_products = products[products['active'] == True].copy()

# Filters
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    categories = ['All'] + sorted(active_products['category'].unique().tolist())
    selected_category = st.selectbox("Category", categories)

with col2:
    search = st.text_input("🔍 Search products", "")

with col3:
    sort_by = st.selectbox("Sort by", ["Name", "Price: Low to High", "Price: High to Low"])

# Filter products
filtered = active_products.copy()
if selected_category != 'All':
    filtered = filtered[filtered['category'] == selected_category]
if search:
    filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

# Sort
if sort_by == "Price: Low to High":
    filtered = filtered.sort_values('price')
elif sort_by == "Price: High to Low":
    filtered = filtered.sort_values('price', ascending=False)
else:
    filtered = filtered.sort_values('name')

st.markdown(f"**{len(filtered)} products found**")
st.markdown("---")

# Display products in grid (3 columns)
cols_per_row = 3
for i in range(0, len(filtered), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(filtered):
            product = filtered.iloc[idx]
            with col:
                # Product card
                st.image(product['image_url'], use_container_width=True)
                st.subheader(product['name'])
                st.write(f"**{product['price']:.2f} {product['currency']}**")
                st.caption(f"Category: {product['category']}")
                st.caption(f"Stock: {product['stock']} units")
                
                # View details button
                if st.button(f"View Details", key=f"view_{product['id']}"):
                    # Send product_view event to Kafka
                    st.session_state.events.emit_view(
                        client_id=st.session_state.user_id,
                        produit_id=int(product['id']),
                        session_id=st.session_state.session_id,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
                    # Store selected product and navigate
                    st.session_state.selected_product_id = int(product['id'])
                    st.switch_page("pages/2_Product_Detail.py")
                
                st.markdown("---")