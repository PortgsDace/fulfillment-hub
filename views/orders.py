import streamlit as st
import pandas as pd
from src.database import query_db
from src.constants import *
from src.helpers import calculate_sla_status

st.title("Orders")

c1, c2, c3 = st.columns(3)
search_query = c1.text_input("Search Order ID or SKU")
filter_status = c2.selectbox("Filter Status", ["ALL"] + [STATUS_NEW, STATUS_PICKING, STATUS_PACKING, STATUS_STAGED, STATUS_SHIPPED, STATUS_BLOCKED])
filter_priority = c3.selectbox("Filter Priority", ["ALL", PRIORITY_NORMAL, PRIORITY_URGENT])

query = "SELECT * FROM orders WHERE 1=1"
params = []

if search_query:
    query += " AND (order_id LIKE ? OR sku LIKE ?)"
    params.extend([f"%{search_query}%", f"%{search_query}%"])
if filter_status != "ALL":
    query += " AND status = ?"
    params.append(filter_status)
if filter_priority != "ALL":
    query += " AND priority = ?"
    params.append(filter_priority)

query += " ORDER BY order_time DESC"

df = query_db(query, params)

if not df.empty:
    df['SLA Status'] = df.apply(lambda r: calculate_sla_status(r['sla_deadline']) if r['priority'] == PRIORITY_URGENT else 'N/A', axis=1)
    
    def highlight_priority(val):
        if val == PRIORITY_URGENT:
            return 'background-color: #ffcccc'
        return ''

    display_df = df[['order_id', 'priority', 'customer_name', 'product_name', 'status', 'SLA Status', 'courier']].copy()
    display_df.columns = ['Order ID', 'Priority', 'Customer', 'Items', 'Status', 'SLA Status', 'Courier']
    
    # Selection logic for order detail
    selected = st.selectbox("Select an order to view details:", display_df['Order ID'].tolist())
    
    st.dataframe(display_df.style.map(highlight_priority, subset=['Priority']), hide_index=True, use_container_width=True)
    
    if selected:
        st.markdown("---")
        from views.order_detail import show_order_detail
        show_order_detail(selected)
else:
    st.info("No orders found matching criteria.")
