import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canteen.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL,
            is_veg INTEGER DEFAULT 1,
            is_available INTEGER DEFAULT 1
        )
    ''')

    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_token TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            username TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT DEFAULT 'Received',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_price REAL NOT NULL,
            customizations TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')

    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Check if menu_items needs seeding
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    if cursor.fetchone()[0] == 0:
        seed_menu_items(cursor)

    conn.commit()
    conn.close()

def seed_menu_items(cursor):
    default_items = [
        (
            'Crispy Masala Dosa',
            'Golden, paper-thin fermented rice crepe stuffed with spiced potato masala, served with 3 chutneys & piping hot sambar.',
            60.0,
            'Breakfast & Tiffin',
            'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=600&q=80',
            1,
            1
        ),
        (
            'Steamed Idli (2 Pcs)',
            'Pillowy soft steamed rice & lentil cakes served with freshly ground coconut chutney and tangy vegetable sambar.',
            40.0,
            'Breakfast & Tiffin',
            'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=600&q=80',
            1,
            1
        ),
        (
            'Crispy Medu Vada (2 Pcs)',
            'Traditional golden fried lentil donuts with a crunchy crust and fluffy center, infused with black pepper and curry leaves.',
            45.0,
            'Breakfast & Tiffin',
            'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=600&q=80',
            1,
            1
        ),
        (
            'Ghee Ven Pongal',
            'Comforting, fragrant rice & yellow moong dal porridge cooked in pure desi ghee, tempered with cashews, cumin, and ginger.',
            55.0,
            'Breakfast & Tiffin',
            'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=600&q=80',
            1,
            1
        ),
        (
            'South Indian Special Meals (Thali)',
            'Full traditional platter with steamed rice, sambar, rasam, kootu, poriyal, curd, appalam, pickle & sweet kesari.',
            120.0,
            'Lunch & Meals',
            'https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?auto=format&fit=crop&w=600&q=80',
            1,
            1
        ),
        (
            'South Indian Filter Coffee',
            'Authentic chicory-infused decoction brewed with rich foamy whole milk, served in a traditional brass tumbler & davarah.',
            25.0,
            'Beverages',
            'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80',
            1,
            1
        )
    ]

    cursor.executemany('''
        INSERT INTO menu_items (name, description, price, category, image_url, is_veg, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', default_items)

# User Helpers
def create_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_db()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True, "Registration successful! Please log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different one."
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    return user

def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Menu Helpers
def get_menu_items(category=None):
    conn = get_db()
    cursor = conn.cursor()
    if category and category != 'All':
        cursor.execute('SELECT * FROM menu_items WHERE category = ? AND is_available = 1 ORDER BY id ASC', (category,))
    else:
        cursor.execute('SELECT * FROM menu_items WHERE is_available = 1 ORDER BY id ASC')
    items = cursor.fetchall()
    conn.close()
    return items

def get_menu_item_by_id(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

# Order Helpers
def create_order(user_id, username, items, total_amount, payment_method):
    import random
    import time
    conn = get_db()
    cursor = conn.cursor()

    order_token = f"CAN-{random.randint(1000, 9999)}"

    cursor.execute('''
        INSERT INTO orders (order_token, user_id, username, total_amount, payment_method, status)
        VALUES (?, ?, ?, ?, ?, 'Received')
    ''', (order_token, user_id, username, total_amount, payment_method))

    order_id = cursor.lastrowid

    for it in items:
        cursor.execute('''
            INSERT INTO order_items (order_id, item_name, quantity, price, total_price, customizations)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            it['name'],
            it['quantity'],
            it['price'],
            it['total_price'],
            it.get('customizations', '')
        ))

    conn.commit()
    conn.close()
    return order_id, order_token

def get_orders_for_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    orders = cursor.fetchall()

    result = []
    for order in orders:
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],))
        items = cursor.fetchall()
        result.append({
            'order': order,
            'items': items
        })
    conn.close()
    return result

def get_order_by_id(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return None

    cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
    items = cursor.fetchall()
    conn.close()
    return {
        'order': order,
        'items': items
    }

# Feedback Helpers
def add_feedback(user_id, username, rating, comments):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (user_id, username, rating, comments)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, rating, comments.strip()))
    conn.commit()
    conn.close()

def get_recent_feedback(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    feedback_list = cursor.fetchall()
    conn.close()
    return feedback_list
