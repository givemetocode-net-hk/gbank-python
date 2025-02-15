import sqlite3

def get_db_connection():
    conn = sqlite3.connect('bank.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_initial_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert initial admin user with username 'root' and password 'root'
    cursor.execute('INSERT INTO users (username, password, balance, role) VALUES (?, ?, ?, ?)',
                   ('root', 'root', 1000.0, 'admin'))
    cursor.execute('INSERT INTO users (username, password, balance, role) VALUES (?, ?, ?, ?)',
                   ('user1', 'user1pass', 500.0, 'user'))
    cursor.execute('INSERT INTO users (username, password, balance, role) VALUES (?, ?, ?, ?)',
                   ('user2', 'user2pass', 300.0, 'user'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()          # Create the database tables
    insert_initial_data()    # Insert initial data if needed
    print("Database setup complete.")