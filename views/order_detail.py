import streamlit as st
from src.database import query_db
from src.services import update_order_status, get_inventory, reserve_inventory, confirm_pick, create_exception
from src.constants import *

def show_order_detail(order_id):
    order = query_db("SELECT * FROM orders WHERE order_id = ?", (order_id,)).iloc[0]
    
    st.subheader(f"ORDER {order['order_id']}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"**Customer:** {order['customer_name']}")
    c2.markdown(f"**Channel:** {order['channel']}")
    c3.markdown(f"**Priority:** {'🔴 ' + order['priority'] if order['priority'] == PRIORITY_URGENT else order['priority']}")
    c4.markdown(f"**Status:** {order['status']}")
    
    st.markdown("### FULFILLMENT PROGRESS")
    stages = [STATUS_NEW, STATUS_PICKING, STATUS_PACKING, STATUS_STAGED, STATUS_SHIPPED]
    try:
        current_idx = stages.index(order['status'])
    except ValueError:
        current_idx = -1
        
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        if i < current_idx:
            cols[i].success(stage)
        elif i == current_idx:
            cols[i].warning(stage)
        else:
            cols[i].info(stage)
            
    st.markdown("### PRODUCT DETAILS")
    st.write(f"**SKU:** {order['sku']} | **Product:** {order['product_name']} | **Variant:** {order['variant']} | **Qty:** {order['quantity']}")
    
    inv = get_inventory(order['sku'], WAREHOUSE_MAIN)
    if inv:
        avail = inv['quantity'] - inv['reserved_quantity']
        st.write(f"**Main Warehouse Available:** {avail}")
    else:
        avail = 0
        st.write("**Main Warehouse Available:** 0")
        
    st.markdown("### ACTIONS")
    
    action_cols = st.columns(4)
    
    if order['status'] == STATUS_NEW:
        if action_cols[0].button("Start Picking", key="start_pick", type="primary"):
            if avail >= order['quantity']:
                update_order_status(order_id, STATUS_PICKING)
                reserve_inventory(order['sku'], WAREHOUSE_MAIN, order['quantity'])
                st.success("Picking started.")
                st.rerun()
            else:
                st.error("Not enough stock in Main Warehouse.")
                update_order_status(order_id, STATUS_BLOCKED)
                create_exception(order_id, "OUT_OF_STOCK", "Insufficient main warehouse inventory", SEVERITY_HIGH)
                st.rerun()
                
    elif order['status'] == STATUS_BLOCKED:
        if action_cols[0].button("Retry Picking", key="retry_pick", type="primary"):
            if avail >= order['quantity']:
                update_order_status(order_id, STATUS_PICKING)
                reserve_inventory(order['sku'], WAREHOUSE_MAIN, order['quantity'])
                st.success("Picking started.")
                st.rerun()
            else:
                st.error("Still not enough stock.")
                
    elif order['status'] == STATUS_PICKING:
        if action_cols[0].button("Mark Picked", key="mark_picked", type="primary"):
            update_order_status(order_id, STATUS_PACKING)
            confirm_pick(order['sku'], WAREHOUSE_MAIN, order['quantity'])
            st.success("Order picked.")
            st.rerun()
            
    elif order['status'] == STATUS_PACKING:
        loc = action_cols[1].text_input("Staging Location (e.g. Rack A1)")
        if action_cols[0].button("Move to Staging", key="mark_staged", type="primary"):
            if loc:
                update_order_status(order_id, STATUS_STAGED, loc)
                st.success("Order staged.")
                st.rerun()
            else:
                st.error("Provide a staging location.")
                
    elif order['status'] == STATUS_STAGED:
        if action_cols[0].button("Mark Shipped", key="mark_shipped", type="primary"):
            update_order_status(order_id, STATUS_SHIPPED)
            st.success("Order shipped.")
            st.rerun()
            
    if order['status'] not in [STATUS_SHIPPED, STATUS_CANCELLED]:
        if action_cols[3].button("Report Exception", key="report_exc"):
            create_exception(order_id, "OTHER", "Manually reported", SEVERITY_MEDIUM)
            st.warning("Exception reported.")
            st.rerun()
