import datetime
from .database import execute_db, query_db
from .constants import *

def get_order(order_id):
    df = query_db("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    if len(df) > 0:
        return df.iloc[0].to_dict()
    return None

def update_order_status(order_id, new_status, staging_location=None):
    if staging_location:
        execute_db("UPDATE orders SET status = ?, staging_location = ?, updated_at = ? WHERE order_id = ?", 
                  (new_status, staging_location, datetime.datetime.now().isoformat(), order_id))
    else:
        execute_db("UPDATE orders SET status = ?, updated_at = ? WHERE order_id = ?", 
                  (new_status, datetime.datetime.now().isoformat(), order_id))

def get_inventory(sku, warehouse=WAREHOUSE_MAIN):
    df = query_db("SELECT * FROM inventory WHERE sku = ? AND warehouse = ?", (sku, warehouse))
    if len(df) > 0:
        return df.iloc[0].to_dict()
    return None

def reserve_inventory(sku, warehouse, qty):
    execute_db("UPDATE inventory SET reserved_quantity = reserved_quantity + ? WHERE sku = ? AND warehouse = ?", (qty, sku, warehouse))

def confirm_pick(sku, warehouse, qty):
    execute_db("UPDATE inventory SET quantity = quantity - ?, reserved_quantity = reserved_quantity - ? WHERE sku = ? AND warehouse = ?", (qty, qty, sku, warehouse))

def create_exception(order_id, exc_type, desc, severity, owner="Warehouse"):
    import uuid
    execute_db('''
        INSERT INTO exceptions (exception_id, order_id, type, description, severity, status, created_at, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4())[:8], order_id, exc_type, desc, severity, EXCEPTION_STATUS_OPEN, datetime.datetime.now().isoformat(), owner))

def request_transfer(sku, name, qty):
    import uuid
    execute_db('''
        INSERT INTO stock_transfers (transfer_id, sku, product_name, from_warehouse, to_warehouse, quantity, status, requested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4())[:8], sku, name, WAREHOUSE_BACKUP, WAREHOUSE_MAIN, qty, TRANSFER_REQUESTED, datetime.datetime.now().isoformat()))

def complete_transfer(transfer_id):
    transfer = query_db("SELECT * FROM stock_transfers WHERE transfer_id = ?", (transfer_id,))
    if len(transfer) > 0:
        t = transfer.iloc[0]
        execute_db("UPDATE stock_transfers SET status = ?, completed_at = ? WHERE transfer_id = ?", (TRANSFER_COMPLETED, datetime.datetime.now().isoformat(), transfer_id))
        execute_db("UPDATE inventory SET quantity = quantity - ? WHERE sku = ? AND warehouse = ?", (int(t['quantity']), t['sku'], t['from_warehouse']))
        execute_db("UPDATE inventory SET quantity = quantity + ? WHERE sku = ? AND warehouse = ?", (int(t['quantity']), t['sku'], t['to_warehouse']))
