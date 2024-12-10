# database.py
import sqlite3

DATABASE_PATH = 'filesystem.sqlite'

def initialize_database():
    """Initializes the SQLite database with the required tables and sets the root directory."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # SQL schema to create the necessary tables
    schema = '''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid INTEGER,
        oid INTEGER,
        name TEXT,
        size INTEGER DEFAULT 0,
        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        contents BLOB,
        read_permission INTEGER DEFAULT 1,
        write_permission INTEGER DEFAULT 0,
        execute_permission INTEGER DEFAULT 1,
        world_read INTEGER DEFAULT 1,
        world_write INTEGER DEFAULT 0,
        world_execute INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS directories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid INTEGER,                            -- parent directory id
        oid INTEGER,                            -- owner id
        name TEXT NOT NULL,                     -- directory name
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_permission INTEGER DEFAULT 1,
        write_permission INTEGER DEFAULT 0,
        execute_permission INTEGER DEFAULT 1,
        world_read INTEGER DEFAULT 1,
        world_write INTEGER DEFAULT 0,
        world_execute INTEGER DEFAULT 1
    );
    CREATE TABLE  IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    '''

    cursor.executescript(schema)

    # Check if the root directory already exists
    cursor.execute('SELECT id FROM directories WHERE id = 1')
    root_dir = cursor.fetchone()

    # If the root directory doesn't exist, insert it
    if not root_dir:
        cursor.execute('''
            INSERT INTO directories (id, pid, oid, name, created_at, modified_at)
            VALUES (1, NULL, 1, '/', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''')
        print("Root directory '/' created with ID 1.")

    conn.commit()
    conn.close()

    print("Database initialized with the required tables.")
