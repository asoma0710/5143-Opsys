import sqlite3

DATABASE_PATH = 'filesystem.sqlite'

def update_existing_file_sizes():
    """Recalculate and update the size of all existing files in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Update the size column for each file based on the length of its contents
    cursor.execute('''
        UPDATE files
        SET size = LENGTH(contents)
        WHERE contents IS NOT NULL
    ''')

    conn.commit()
    conn.close()

    print("File sizes updated for all existing files.")

# Call the function to update file sizes
update_existing_file_sizes()
