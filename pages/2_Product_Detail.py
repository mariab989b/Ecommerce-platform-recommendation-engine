import streamlit as st
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Product Details", page_icon="🔍", layout="wide")

# Check if product is selected
if 'selected_product_id' not in st.session_state:
    st.warning("Please select a product from the catalog first")
    if st.button("Go to Catalog"):
        st.switch_page("pages/1_Catalog.py")
    st.stop()

# Load product details
products = st.session_state.store.read('products')
product = products[products['id'] == st.session_state.selected_product_id].iloc[0]

# Back button
if st.button("← Back to Catalog"):
    st.switch_page("pages/1_Catalog.py")

st.title(product['name'])

# Product details section
col1, col2 = st.columns([1, 1])

with col1:
    st.image(product['image_url'], use_container_width=True)

with col2:
    st.markdown(f"### {product['price']:.2f} {product['currency']}")
    st.markdown(f"**Category:** {product['category']}")
    st.markdown(f"**Stock:** {product['stock']} units available")
    st.markdown(f"**Status:** {'✅ In Stock' if product['stock'] > 0 else '❌ Out of Stock'}")
    
    st.markdown("---")
    
    # Quantity selector
    quantity = st.number_input("Quantity", min_value=1, max_value=int(product['stock']), value=1)
    
    # Add to cart button (non-functional for demo)
    if st.button("🛒 Add to Cart", type="primary", disabled=True):
        st.info("Cart functionality coming soon!")
    
    st.caption("💡 This is a demo - cart is not functional yet")

st.markdown("---")

# Recommendations section
st.subheader("🎯 Recommended Products for You")
st.caption("Based on your browsing history and similar customer preferences")

# TODO: Get recommendations from Redis/PostgreSQL
# For now, show random products from same category
same_category = products[
    (products['category'] == product['category']) & 
    (products['id'] != product['id']) &
    (products['active'] == True)
].head(3)

if len(same_category) > 0:
    cols = st.columns(len(same_category))
    for idx, col in enumerate(cols):
        with col:
            reco = same_category.iloc[idx]
            st.image(reco['image_url'], use_container_width=True)
            st.markdown(f"**{reco['name']}**")
            st.markdown(f"{reco['price']:.2f} {reco['currency']}")
            if st.button(f"View", key=f"reco_{reco['id']}"):
                # Send view event
                st.session_state.events.emit_view(
                    client_id=st.session_state.user_id,
                    produit_id=int(reco['id']),
                    session_id=st.session_state.session_id,
                    timestamp=datetime.utcnow().isoformat()
                )
                st.session_state.selected_product_id = int(reco['id'])
                st.rerun()
else:
    st.info("No recommendations available yet. Keep browsing!")

# Real-time recommendation loading simulation
with st.expander("🔄 Loading AI-powered recommendations..."):
    st.write("Analyzing your preferences...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success("Recommendations ready! (Feature coming soon with real ML model)")