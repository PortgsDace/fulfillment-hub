import streamlit as st
from src.database import query_db
from src.services import update_order_status
from src.constants import *

st.title("Staging")
st.markdown("### Packages waiting for courier pickup")

df = query_db("SELECT * FROM orders WHERE status = ?", (STATUS_STAGED,))

if not df.empty:
    for idx, row in df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Order:** {row['order_id']}")
            c2.markdown(f"**Courier:** {row['courier']}")
            c3.markdown(f"**Location:** {row['staging_location']}")
            
            if c4.button("Mark Picked Up", key=f"pk_{row['order_id']}", type="primary"):
                update_order_status(row['order_id'], STATUS_SHIPPED)
                st.success("Marked as Shipped!")
                st.rerun()
else:
    st.success("No packages waiting in staging.")
