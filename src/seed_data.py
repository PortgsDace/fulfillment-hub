import sqlite3
import random
import uuid
import datetime
from .database import get_db_connection, init_db
from .constants import *

def seed_db():
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] > 0:
        conn.close()
        return
        
    products_data = [
        ("SKU-001", "Classic Hoodie", "Black / M", "Apparel", 1499),
        ("SKU-002", "Classic Hoodie", "Black / L", "Apparel", 1499),
        ("SKU-003", "Running Shorts", "Navy / M", "Apparel", 899),
        ("SKU-004", "Running Shorts", "Navy / L", "Apparel", 899),
        ("SKU-005", "Water Bottle", "1L / Silver", "Accessories", 499),
        ("SKU-006", "Yoga Mat", "Purple", "Equipment", 1299),
        ("SKU-007", "Dumbbells", "5kg / Pair", "Equipment", 2499),
        ("SKU-008", "Jump Rope", "Adjustable", "Equipment", 299),
        ("SKU-009", "Gym Bag", "Black", "Accessories", 1999),
        ("SKU-010", "Protein Powder", "Chocolate / 1kg", "Nutrition", 3499),
    ]
    
    for sku, name, variant, cat, price in products_data:
        c.execute('''
            INSERT INTO products (product_id, sku, product_name, variant, category, unit_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4())[:8], sku, name, variant, cat, price))
        
        # Main Warehouse
        main_qty = random.randint(10, 50)
        # Force scenario C: Main warehouse 0, Backup > 0
        if sku == "SKU-005":
            main_qty = 0
            backup_qty = 15
        else:
            backup_qty = random.randint(0, 20)
            
        c.execute('''
            INSERT INTO inventory (inventory_id, sku, warehouse, quantity, reserved_quantity, reorder_level, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4())[:8], sku, WAREHOUSE_MAIN, main_qty, random.randint(0, 5), 10, datetime.datetime.now().isoformat()))
        
        c.execute('''
            INSERT INTO inventory (inventory_id, sku, warehouse, quantity, reserved_quantity, reorder_level, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4())[:8], sku, WAREHOUSE_BACKUP, backup_qty, 0, 5, datetime.datetime.now().isoformat()))
        
    customers = ["Rahul Sharma", "Priya Patel", "Amit Singh", "Neha Gupta", "Vikram Kumar", "Sneha Reddy"]
    couriers = ["BlueDart", "Delhivery", "FedEx", "Ecom Express"]
    locations = ["Rack A1", "Rack B2", "Rack C3", "Rack D4"]
    
    now = datetime.datetime.now()
    
    # Seed 50 orders
    for i in range(1, 51):
        order_id = f"#ORD-{1000+i}"
        customer = random.choice(customers)
        channel = random.choice(["Website", "Amazon", "Flipkart"])
        
        # Scenario logic
        is_priority = (i <= 15)  # roughly 30% priority
        priority = PRIORITY_URGENT if is_priority else PRIORITY_NORMAL
        
        # Scenario A & B
        if i == 1:
            # Overdue priority
            order_time = now - datetime.timedelta(hours=5)
            sla = now - datetime.timedelta(minutes=30)
            status = STATUS_PICKING
        elif i == 2:
            # At risk priority
            order_time = now - datetime.timedelta(hours=2)
            sla = now + datetime.timedelta(minutes=45)
            status = STATUS_NEW
        elif i == 3:
            # Urgent priority
            order_time = now - datetime.timedelta(hours=3)
            sla = now + datetime.timedelta(minutes=15)
            status = STATUS_NEW
        else:
            order_time = now - datetime.timedelta(hours=random.randint(1, 24))
            sla = order_time + datetime.timedelta(hours=4 if is_priority else 48)
            status = random.choice([STATUS_NEW, STATUS_PICKING, STATUS_PACKING, STATUS_STAGED, STATUS_SHIPPED])
            
        sku, name, variant, _, _ = random.choice(products_data)
        if i == 4: # Scenario C target
            sku, name, variant = "SKU-005", "Water Bottle", "1L / Silver"
            status = STATUS_NEW
            
        qty = random.randint(1, 3)
        courier = random.choice(couriers)
        staging = random.choice(locations) if status == STATUS_STAGED else None
        
        # Scenario F: Staged but delayed pickup
        if i == 5:
            status = STATUS_STAGED
            staging = "Rack A1"
            order_time = now - datetime.timedelta(days=1)
            sla = now - datetime.timedelta(hours=10)
            
        c.execute('''
            INSERT INTO orders (order_id, customer_name, channel, order_time, priority, sla_deadline, status, sku, product_name, variant, quantity, warehouse, courier, staging_location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, customer, channel, order_time.isoformat(), priority, sla.isoformat(), status, sku, name, variant, qty, WAREHOUSE_MAIN, courier, staging, order_time.isoformat(), order_time.isoformat()))
        
    # Exceptions
    # Scenario D & H: High severity inventory mismatch
    c.execute('''
        INSERT INTO exceptions (exception_id, order_id, type, description, severity, status, created_at, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4())[:8], "#ORD-1010", "INVENTORY_MISMATCH", "System says 15 units. Physical count says 2.", SEVERITY_HIGH, EXCEPTION_STATUS_OPEN, now.isoformat(), "Warehouse"))
    
    conn.commit()
    conn.close()

def reset_db():
    try:
        os.remove(DB_PATH)
    except:
        pass
    seed_db()
