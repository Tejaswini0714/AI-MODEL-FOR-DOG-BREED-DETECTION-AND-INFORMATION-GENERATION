
import sqlite3

# -----------------------------
# USERS TABLE
# -----------------------------
def create_users_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            profile_pic TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(first_name, last_name, email, password, profile_pic):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (first_name, last_name, email, password, profile_pic)
        VALUES (?, ?, ?, ?, ?)
    ''', (first_name, last_name, email, password, profile_pic))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def login_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, first_name, last_name, email, profile_pic):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET first_name = ?, last_name = ?, email = ?, profile_pic = ?
        WHERE id = ?
    ''', (first_name, last_name, email, profile_pic, user_id))
    conn.commit()
    conn.close()

# -----------------------------
# HISTORY TABLE
# -----------------------------
def create_history_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            breed TEXT,
            confidence REAL,
            img_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_history(user_id, breed, confidence, img_path):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO history (user_id, breed, confidence, img_path)
        VALUES (?, ?, ?, ?)
    ''', (user_id, breed, confidence, img_path))
    conn.commit()
    conn.close()

def get_history_by_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, breed, confidence, img_path, created_at FROM history WHERE user_id=? ORDER BY created_at DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# -----------------------------
# Initialize all tables
# -----------------------------
create_users_table()
create_history_table()
