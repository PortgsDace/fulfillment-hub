import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'fulfillment.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    c = conn.cursor()
    
    # Products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            sku TEXT,
            product_name TEXT,
            variant TEXT,
            category TEXT,
            unit_price INTEGER
        )
    ''')
    
    # Inventory table
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id TEXT PRIMARY KEY,
            sku TEXT,
            warehouse TEXT,
            quantity INTEGER,
            reserved_quantity INTEGER,
            reorder_level INTEGER,
            last_updated TEXT
        )
    ''')
    
    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            channel TEXT,
            order_time TEXT,
            priority TEXT,
            sla_deadline TEXT,
            status TEXT,
            sku TEXT,
            product_name TEXT,
            variant TEXT,
            quantity INTEGER,
            warehouse TEXT,
            courier TEXT,
            tracking_number TEXT,
            shipping_label TEXT,
            staging_location TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Exceptions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exceptions (
            exception_id TEXT PRIMARY KEY,
            order_id TEXT,
            type TEXT,
            description TEXT,
            severity TEXT,
            status TEXT,
            created_at TEXT,
            resolved_at TEXT,
            owner TEXT
        )
    ''')
    
    # Stock Transfers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_transfers (
            transfer_id TEXT PRIMARY KEY,
            sku TEXT,
            product_name TEXT,
            from_warehouse TEXT,
            to_warehouse TEXT,
            quantity INTEGER,
            status TEXT,
            requested_at TEXT,
            completed_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def query_db(query, args=()):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return df

def execute_db(query, args=()):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    conn.close()
