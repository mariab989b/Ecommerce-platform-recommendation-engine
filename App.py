import streamlit as st
import pandas as pd
import uuid
import os
from lib.events import EventDispatcher

st.set_page_config(
    page_title="BuyMe",
    page_icon="🛍️",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
    }
    .stat-card {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }
    .stat-label {
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"anonymous_{str(uuid.uuid4())[:8]}"
if 'cart' not in st.session_state:
    st.session_state.cart = {}

@st.cache_data
def load_products():
    paths = ['/app/data/produit.csv', 'data/produit.csv']
    for path in paths:
        try:
            if os.path.exists(path):
                df = pd.read_csv(path)
                df = df.rename(columns={
                    'ID': 'id',
                    'Product_Name': 'name',
                    'Price': 'price',
                    'Category': 'category',
                    'Stock_Quantity': 'stock',
                    'Path_image': 'image_url'
                })
                df['active'] = True
                df['currency'] = 'EUR'
                return df
        except:
            continue
    st.error("Could not load products")
    st.stop()

@st.cache_data
def load_users():
    return pd.DataFrame([
        {"id": 1, "email": "admin@buyme.com", "password": "admin123", "role": "admin"},
        {"id": 2, "email": "alice@demo.com", "password": "alice123", "role": "customer"},
        {"id": 3, "email": "bob@demo.com", "password": "bob123", "role": "customer"},
    ])

if 'products' not in st.session_state:
    st.session_state.products = load_products()
    st.session_state.users = load_users()
    st.session_state.events = EventDispatcher(backend='kafka', store=None, kafka_conf={})

# Sidebar
with st.sidebar:
    st.markdown("### Account")
    
    if st.session_state.user is None:
        st.info("Guest Mode")
        
        with st.expander("Sign In"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.button("Sign In", type="primary"):
                users = st.session_state.users
                match = users[(users['email'].str.lower() == email.lower()) & (users['password'] == password)]
                
                if not match.empty:
                    st.session_state.user = match.iloc[0].to_dict()
                    st.session_state.user_id = f"user_{match.iloc[0]['id']}"
                    st.success("Signed in")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.caption("Demo: alice@demo.com / alice123")
    else:
        st.success("Signed in")
        st.write(f"**{st.session_state.user['email']}**")
        
        if st.button("Sign Out"):
            st.session_state.user = None
            st.session_state.user_id = f"anonymous_{str(uuid.uuid4())[:8]}"
            st.rerun()

# Main
st.markdown('<h1 class="main-header">BuyMe</h1>', unsafe_allow_html=True)
st.markdown("---")

products = st.session_state.products

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(products)}</div>
        <div class="stat-label">Products</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{products['category'].nunique()}</div>
        <div class="stat-label">Categories</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    status = "Authenticated" if st.session_state.user else "Guest"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{status}</div>
        <div class="stat-label">Status</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.info("Navigate to Product Catalog in the sidebar")