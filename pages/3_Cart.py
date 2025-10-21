import streamlit as st

st.set_page_config(page_title="Shopping Cart", page_icon="🛒", layout="wide")

st.title("🛒 Your Shopping Cart")

if not st.session_state.cart or len(st.session_state.cart) == 0:
    st.info("Your cart is empty. Start shopping!")
    if st.button("Go to Catalog"):
        st.switch_page("pages/1_Catalog.py")
else:
    st.write("Cart items will appear here (feature coming soon)")
    
    if st.button("← Continue Shopping"):
        st.switch_page("pages/1_Catalog.py")
