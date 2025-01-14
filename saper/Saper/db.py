import sqlite3
from Saper.constants import DATABASE_NAME

def initialize_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_time INTEGER,
            result TEXT CHECK(result IN ('win', 'loss', 'incomplete')),
            found_mines INTEGER,
            total_mines INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

def log_game(username, game_time, result, found_mines, total_mines):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO games (username, game_time, result, found_mines, total_mines)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, game_time, result, found_mines, total_mines))
    conn.commit()
    conn.close()

def get_statistics():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, COUNT(*), 
               SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
               AVG(game_time) as average_time
        FROM games
        GROUP BY username
    ''')
    stats = cursor.fetchall()
    conn.close()
    return stats 