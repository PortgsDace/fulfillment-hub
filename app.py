import streamlit as st
from src.seed_data import seed_db
import os

st.set_page_config(
    page_title="Fulfillment Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
if not os.path.exists('data/fulfillment.db'):
    seed_db()

# Navigation
pages = {
    "📊 Control Tower": "views/control_tower.py",
    "📦 Orders": "views/orders.py",
    "🛒 Picking": "views/picking.py",
    "🏬 Inventory": "views/inventory.py",
    "🚚 Staging": "views/staging.py",
    "🚨 Exceptions": "views/exceptions.py"
}

st.sidebar.title("FULFILLMENT HUB")
st.sidebar.markdown("---")

selection = st.sidebar.radio("Navigation", list(pages.keys()))

st.sidebar.markdown("---")
if st.sidebar.button("Reset Demo Data"):
    from src.seed_data import reset_db
    reset_db()
    st.sidebar.success("Database Reset!")
    st.rerun()

st.sidebar.info("System Status: Online")

page_path = pages[selection]
with open(page_path, "r", encoding='utf-8') as f:
    exec(f.read())
