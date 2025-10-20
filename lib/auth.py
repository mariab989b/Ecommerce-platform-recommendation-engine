
## lib/auth.py

import streamlit as st
import pandas as pd
from lib.data_io import ExcelStore

USERS = 'users'

ROLE_ADMIN = 'admin'
ROLE_CUSTOMER = 'customer'


def get_session_user():
    return st.session_state.get('user')


def is_authenticated() -> bool:
    return 'user' in st.session_state and st.session_state['user'] is not None


def require_role(role: str) -> bool:
    u = get_session_user()
    return bool(u and u.get('role') == role)


def login(store: ExcelStore, email: str, password: str) -> bool:
    users = store.read(USERS)
    ok = users[(users['email'] == email) & (users['password'] == password)]
    if not ok.empty:
        user = ok.iloc[0].to_dict()
        st.session_state['user'] = user
        return True
    return False


def logout():
    st.session_state.pop('user', None)
    st.session_state.pop('cart', None)  # reset cart on logout


def signup(store: ExcelStore, email: str, password: str) -> bool:
    users = store.read(USERS)
    if (users['email'] == email).any():
        return False
    new_id = store.next_id(USERS)
    store.append(USERS, {
        'id': new_id,
        'email': email,
        'password': password,
        'role': ROLE_CUSTOMER,
    })
    return True
