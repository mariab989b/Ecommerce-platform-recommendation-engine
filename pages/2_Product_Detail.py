import streamlit as st
from datetime import datetime
import base64
from pathlib import Path

st.set_page_config(page_title="Product Details", layout="wide")

if 'products' not in st.session_state:
    st.error("Please return to home page")
    st.stop()

if 'selected_product_id' not in st.session_state:
    st.error("Please select a product")
    st.stop()

def load_image(image_path):
    if image_path and Path(image_path).exists():
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    return None

products = st.session_state.products
product = products[products['id'] == st.session_state.selected_product_id].iloc[0]

if st.button("← Back"):
    st.switch_page("pages/1_Catalog.py")

st.title(product['name'])
st.caption(f"ID: {product['id']} | Category: {product['category']}")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    img = load_image(product['image_url'])
    if img:
        st.markdown(f'<img src="data:image/png;base64,{img}" style="width:100%; border-radius:10px; border:1px solid #e5e7eb;"/>', unsafe_allow_html=True)
    else:
        st.image("https://via.placeholder.com/500x500", use_container_width=True)

with col2:
    st.markdown(f"### {product['price']:.2f} EUR")
    st.write(f"**Category:** {product['category']}")
    st.write(f"**Stock:** {product['stock']} units")
    
    if product['stock'] > 50:
        st.success("In Stock")
    elif product['stock'] > 0:
        st.warning(f"{product['stock']} remaining")
    else:
        st.error("Out of Stock")
    
    st.markdown("---")
    
    if product['stock'] > 0:
        qty = st.number_input("Quantity", 1, int(product['stock']), 1)
        
        if st.button("Add to Cart", type="primary"):
            if product['id'] not in st.session_state.cart:
                st.session_state.cart[product['id']] = 0
            st.session_state.cart[product['id']] += qty
            st.success(f"Added {qty}x {product['name']}")

st.markdown("---")
st.subheader("Recommended Products")

same_cat = products[
    (products['category'] == product['category']) & 
    (products['id'] != product['id']) &
    (products['active'] == True)
].head(3)

if len(same_cat) > 0:
    cols = st.columns(len(same_cat))
    
    for idx, col in enumerate(cols):
        with col:
            r = same_cat.iloc[idx]
            
            img = load_image(r['image_url'])
            if img:
                st.markdown(f'<img src="data:image/png;base64,{img}" style="width:100%; border-radius:8px;"/>', unsafe_allow_html=True)
            else:
                st.image("https://via.placeholder.com/300x300", use_container_width=True)
            
            st.write(f"**{r['name']}**")
            st.write(f"{r['price']:.2f} EUR")
            
            if st.button("View", key=f"r_{r['id']}"):
                try:
                    st.session_state.events.emit_view(
                        client_id=st.session_state.user_id,
                        produit_id=int(r['id']),
                        session_id=st.session_state.session_id,
                        timestamp=datetime.utcnow().isoformat()
                    )
                except:
                    pass
                
                st.session_state.selected_product_id = int(r['id'])
                st.rerun()
else:
    st.info("No similar products available")