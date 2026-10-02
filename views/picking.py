import streamlit as st
from src.database import query_db
from src.services import update_order_status, confirm_pick, create_exception
from src.constants import *
from src.helpers import get_priority_score

st.title("Picking")
st.markdown("### Orders Ready to Pick")

df = query_db("SELECT * FROM orders WHERE status = ?", (STATUS_PICKING,))

if not df.empty:
    df['score'] = df.apply(get_priority_score, axis=1)
    df = df.sort_values('score', ascending=False)
    
    for idx, row in df.iterrows():
        with st.container(border=True):
            st.subheader(f"ORDER {row['order_id']}")
            if row['priority'] == PRIORITY_URGENT:
                st.error("🔴 PRIORITY")
                
            c1, c2 = st.columns(2)
            c1.markdown(f"**Product:** {row['product_name']}<br>**Variant:** <span style='font-size:1.2em;font-weight:bold;color:blue;'>{row['variant']}</span>", unsafe_allow_html=True)
            c2.markdown(f"**Quantity:** {row['quantity']}<br>**Location:** MAIN WAREHOUSE", unsafe_allow_html=True)
            
            c3, c4, c5 = st.columns(3)
            confirm = c3.checkbox(f"Confirm picked {row['quantity']}x {row['variant']}", key=f"chk_{row['order_id']}")
            
            if c3.button("MARK PICKED", key=f"btn_{row['order_id']}", type="primary", use_container_width=True):
                if confirm:
                    update_order_status(row['order_id'], STATUS_PACKING)
                    confirm_pick(row['sku'], WAREHOUSE_MAIN, row['quantity'])
                    st.success("Picked successfully.")
                    st.rerun()
                else:
                    st.error("Please confirm the variant.")
                    
            if c4.button("REPORT STOCK ISSUE", key=f"iss_{row['order_id']}", use_container_width=True):
                create_exception(row['order_id'], "INVENTORY_MISMATCH", "Reported during picking", SEVERITY_HIGH)
                update_order_status(row['order_id'], STATUS_BLOCKED)
                st.warning("Issue reported. Order Blocked.")
                st.rerun()
else:
    st.success("No orders waiting for picking!")
