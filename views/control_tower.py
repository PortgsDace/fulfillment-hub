import streamlit as st
import pandas as pd
from src.database import query_db
from src.helpers import calculate_sla_status
from src.constants import *

st.title("Control Tower")
st.markdown("##### Everything that needs attention, in one place.")

if st.button("🚀 Simulate Incoming Priority Order", type="primary"):
    import uuid, datetime, random
    from src.database import execute_db
    
    order_id = f"#ORD-SIM-{random.randint(1000,9999)}"
    now = datetime.datetime.now()
    sla = now + datetime.timedelta(minutes=45)
    
    execute_db('''
        INSERT INTO orders (order_id, customer_name, channel, order_time, priority, sla_deadline, status, sku, product_name, variant, quantity, warehouse, courier, staging_location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, "Test User", "Simulation", now.isoformat(), PRIORITY_URGENT, sla.isoformat(), STATUS_NEW, "SKU-005", "Water Bottle", "1L / Silver", 5, WAREHOUSE_MAIN, "FastTrack", None, now.isoformat(), now.isoformat()))
    st.success(f"Incoming Priority Order {order_id} arrived! Stock will be checked during picking.")
    st.rerun()

# KPI Calculations
df_orders = query_db("SELECT * FROM orders WHERE status != ?", (STATUS_SHIPPED,))
df_shipped = query_db("SELECT * FROM orders WHERE status = ?", (STATUS_SHIPPED,))
df_exceptions = query_db("SELECT * FROM exceptions WHERE status = ?", (EXCEPTION_STATUS_OPEN,))
df_inventory = query_db("SELECT * FROM inventory")

today_orders = len(df_orders) + len(df_shipped)
priority_orders = len(df_orders[df_orders['priority'] == PRIORITY_URGENT])
blocked_orders = len(df_orders[df_orders['status'] == STATUS_BLOCKED])
waiting_pickup = len(df_orders[df_orders['status'] == STATUS_STAGED])

at_risk = 0
for idx, row in df_orders.iterrows():
    status = calculate_sla_status(row['sla_deadline'])
    if status in ["OVERDUE", "URGENT", "AT RISK"]:
        at_risk += 1

low_stock = 0
for idx, row in df_inventory.iterrows():
    available = row['quantity'] - row['reserved_quantity']
    if available <= row['reorder_level']:
        low_stock += 1

# Display KPIs
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Orders Today", today_orders)
c2.metric("Priority Orders", priority_orders)
c3.metric("At Risk", at_risk, delta="-Urgent" if at_risk>0 else None, delta_color="inverse")
c4.metric("Blocked", blocked_orders)
c5.metric("Low Stock", low_stock)
c6.metric("Waiting for Pickup", waiting_pickup)

st.markdown("---")
c_left, c_right = st.columns([1, 1])

with c_left:
    st.subheader("Needs Attention")
    
    if at_risk > 0:
        st.error(f"🔴 {at_risk} priority orders at risk")
    if len(df_exceptions) > 0:
        high_sev = len(df_exceptions[df_exceptions['severity'] == SEVERITY_HIGH])
        if high_sev > 0:
            st.error(f"🔴 {high_sev} high-severity exception(s)")
        else:
            st.warning(f"🟠 {len(df_exceptions)} open exception(s)")
    if waiting_pickup > 0:
        st.warning(f"🟠 {waiting_pickup} packages waiting for pickup")
        
    st.subheader("Fulfillment Pipeline")
    
    pipe_cols = st.columns(5)
    counts = df_orders['status'].value_counts()
    
    pipe_cols[0].metric("NEW", counts.get(STATUS_NEW, 0))
    pipe_cols[1].metric("PICKING", counts.get(STATUS_PICKING, 0))
    pipe_cols[2].metric("PACKING", counts.get(STATUS_PACKING, 0))
    pipe_cols[3].metric("STAGED", counts.get(STATUS_STAGED, 0))
    pipe_cols[4].metric("SHIPPED", len(df_shipped))

with c_right:
    st.subheader("Priority Orders")
    
    pri_df = df_orders[df_orders['priority'] == PRIORITY_URGENT].copy()
    if not pri_df.empty:
        pri_df['Risk'] = pri_df['sla_deadline'].apply(calculate_sla_status)
        # sort by risk manually
        risk_order = {"OVERDUE": 1, "URGENT": 2, "AT RISK": 3, "SAFE": 4}
        pri_df['Risk_Score'] = pri_df['Risk'].map(risk_order)
        pri_df = pri_df.sort_values('Risk_Score')
        
        display_df = pri_df[['order_id', 'customer_name', 'status', 'Risk']].head(5)
        display_df.columns = ['Order', 'Customer', 'Status', 'Risk']
        st.dataframe(display_df, hide_index=True, use_container_width=True)
    else:
        st.info("No active priority orders.")
