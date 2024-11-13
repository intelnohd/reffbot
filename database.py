import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        user_id INTEGER,
        referral_id INTEGER,
        UNIQUE(user_id, referral_id)
    )
    ''')
    conn.commit()
    return conn

# Добавление пользователя
def add_user(user_id, balance=0):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)', (user_id, balance))
    conn.commit()

# Получение информации о пользователе
def get_user(user_id):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    return {'user_id': user[0], 'balance': user[1]} if user else None

# Обновление баланса пользователя
def update_user(user_id, new_balance):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()


def get_top_users(limit=10):
    """Получить топ пользователей с самым высоким балансом."""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT ?', (limit,))
    top_users = cursor.fetchall()
    return [{'user_id': row[0], 'balance': row[1]} for row in top_users]