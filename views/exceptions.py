import streamlit as st
from src.database import query_db, execute_db
from src.constants import *
import datetime

st.title("Exceptions")

df = query_db("SELECT * FROM exceptions WHERE status = ?", (EXCEPTION_STATUS_OPEN,))

if not df.empty:
    for idx, row in df.iterrows():
        with st.container(border=True):
            if row['severity'] == SEVERITY_HIGH:
                st.error(f"🔴 HIGH | {row['type']} | {row['order_id']}")
            elif row['severity'] == SEVERITY_MEDIUM:
                st.warning(f"🟠 MEDIUM | {row['type']} | {row['order_id']}")
            else:
                st.info(f"🔵 LOW | {row['type']} | {row['order_id']}")
                
            st.write(f"**Description:** {row['description']}")
            st.write(f"**Owner:** {row['owner']}")
            
            if st.button("Resolve", key=f"res_{row['exception_id']}"):
                execute_db("UPDATE exceptions SET status = ?, resolved_at = ? WHERE exception_id = ?", 
                          (EXCEPTION_STATUS_RESOLVED, datetime.datetime.now().isoformat(), row['exception_id']))
                st.success("Exception resolved.")
                st.rerun()
else:
    st.success("No open exceptions.")
