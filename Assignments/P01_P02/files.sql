CREATE TABLE IF NOT EXISTS directories (
    dir_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES directories(dir_id) ON DELETE CASCADE,
    UNIQUE(name, parent_id)  -- Ensure that directory names are unique within the same parent
);

CREATE TABLE IF NOT EXISTS files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER, -- References directories
    is_directory BOOLEAN NOT NULL,
    size INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES directories(dir_id) ON DELETE CASCADE,
    UNIQUE(name, parent_id)  -- Ensure that file names are unique within the same directory
);

-- Choose one of the following options based on your use case:

-- Option 1: Store file contents as chunks (useful for large files)
CREATE TABLE IF NOT EXISTS file_contents (
    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    chunk BLOB, -- Each file's content is split into chunks for efficient storage
    chunk_index INTEGER,
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
);

-- OR Option 2: Store file contents as text (for smaller files)
-- CREATE TABLE IF NOT EXISTS file_contents (
--    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
--    file_id INTEGER NOT NULL,
--    content TEXT,  -- Stores the actual file content as text
--    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
-- );

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    perm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER,
    dir_id INTEGER,
    user_id INTEGER,
    read_permission BOOLEAN DEFAULT 0,
    write_permission BOOLEAN DEFAULT 0,
    execute_permission BOOLEAN DEFAULT 0,
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (dir_id) REFERENCES directories(dir_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
