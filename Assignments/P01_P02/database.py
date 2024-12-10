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
        pid INTEGER,                            -- parent directory id
        oid INTEGER,                            -- owner id
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

    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Trigger for Insert: Automatically update file size after a file is inserted
    CREATE TRIGGER IF NOT EXISTS update_file_size_after_insert
    AFTER INSERT ON files
    FOR EACH ROW
    BEGIN
        UPDATE files
        SET size = LENGTH(NEW.contents)
        WHERE id = NEW.id;
    END;

    -- Trigger for Update: Automatically update file size and modified date after the file contents are modified
    CREATE TRIGGER IF NOT EXISTS update_file_size_after_update
    AFTER UPDATE OF contents ON files
    FOR EACH ROW
    BEGIN
        UPDATE files
        SET size = LENGTH(NEW.contents),
            modified_date = CURRENT_TIMESTAMP
        WHERE id = NEW.id;

        -- Ensure the parent directory's modified_at date is updated when a file in the directory is modified
        UPDATE directories
        SET modified_at = CURRENT_TIMESTAMP
        WHERE id = NEW.pid;
    END;

    -- Trigger to update the modified_at of a directory whenever a new file is inserted into it
    CREATE TRIGGER IF NOT EXISTS update_directory_after_insert_file
    AFTER INSERT ON files
    FOR EACH ROW
    BEGIN
        UPDATE directories
        SET modified_at = CURRENT_TIMESTAMP
        WHERE id = NEW.pid;
    END;

    -- Trigger to update the modified_at of a directory whenever a new subdirectory is inserted into it
    CREATE TRIGGER IF NOT EXISTS update_directory_after_insert_subdir
    AFTER INSERT ON directories
    FOR EACH ROW
    BEGIN
        UPDATE directories
        SET modified_at = CURRENT_TIMESTAMP
        WHERE id = NEW.pid;
    END;

    -- Trigger to update the modified_at of a directory when it's directly modified (name, permissions, etc.)
    CREATE TRIGGER IF NOT EXISTS update_directory_after_update
    AFTER UPDATE ON directories
    FOR EACH ROW
    BEGIN
        UPDATE directories
        SET modified_at = CURRENT_TIMESTAMP
        WHERE id = NEW.id;
    END;
    '''

    cursor.executescript(schema)

    # Check if the root directory already exists
    cursor.execute('SELECT id FROM directories WHERE id = 1')
    root_dir = cursor.fetchone()

    # If the root directory doesn't exist, insert it
    if not root_dir:
        cursor.execute('''
            INSERT INTO directories (id, pid, oid, name, created_at, modified_at)
            VALUES (1, NULL, 1, 'root', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''')
        print("Root directory '/' created with ID 1.")

    conn.commit()
    conn.close()

    print("Database initialized with the required tables and triggers.")

if __name__ == '__main__':
    initialize_database()
