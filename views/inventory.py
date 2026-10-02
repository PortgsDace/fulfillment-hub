import streamlit as st
import pandas as pd
from src.database import query_db
from src.services import request_transfer, complete_transfer
from src.constants import *

st.title("Inventory")

search_q = st.text_input("Search SKU or Product")

q = '''
    SELECT i.sku, p.product_name, p.variant, 
           MAX(CASE WHEN i.warehouse = 'MAIN' THEN i.quantity - i.reserved_quantity ELSE 0 END) as main_avail,
           MAX(CASE WHEN i.warehouse = 'BACKUP' THEN i.quantity - i.reserved_quantity ELSE 0 END) as backup_avail
    FROM inventory i
    JOIN products p ON i.sku = p.sku
    WHERE i.sku LIKE ? OR p.product_name LIKE ?
    GROUP BY i.sku, p.product_name, p.variant
'''
df = query_db(q, (f"%{search_q}%", f"%{search_q}%"))

st.dataframe(df, hide_index=True, use_container_width=True)

st.markdown("---")
st.subheader("Stock Transfers")

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Request Transfer")
    skus = df['sku'].tolist()
    sel_sku = st.selectbox("Select SKU", skus)
    if sel_sku:
        prod_name = df[df['sku'] == sel_sku]['product_name'].iloc[0]
        qty = st.number_input("Quantity", min_value=1, value=5)
        if st.button("REQUEST TRANSFER", type="primary"):
            request_transfer(sel_sku, prod_name, qty)
            st.success("Transfer requested.")
            st.rerun()

with c2:
    st.markdown("#### Pending Transfers")
    t_df = query_db("SELECT * FROM stock_transfers WHERE status != ?", (TRANSFER_COMPLETED,))
    if not t_df.empty:
        for idx, row in t_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['sku']}** - {row['product_name']} | Qty: {row['quantity']}")
                st.write(f"Status: {row['status']}")
                if st.button("Mark Completed", key=f"t_{row['transfer_id']}"):
                    complete_transfer(row['transfer_id'])
                    st.success("Transfer completed.")
                    st.rerun()
    else:
        st.info("No pending transfers.")
