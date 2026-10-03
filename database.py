import json
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("skincare_cabinet.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            analysis_data TEXT,
            image_url TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_product(name, category, tags, analysis_data, image_url=None):
    conn = sqlite3.connect("skincare_cabinet.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO products (name, category, tags, analysis_data, image_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        name, 
        category, 
        json.dumps(tags, ensure_ascii=False), 
        json.dumps(analysis_data, ensure_ascii=False), 
        image_url,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect("skincare_cabinet.db")
    c = conn.cursor()
    c.execute('SELECT id, name, category, tags, analysis_data, image_url, created_at FROM products ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = sqlite3.connect("skincare_cabinet.db")
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()