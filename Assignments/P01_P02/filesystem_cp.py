import sqlite3
from datetime import datetime
import os  # For handling paths

DATABASE_PATH = 'filesystem.sqlite'

class FileSystem:
    def __init__(self):
        self.current_dir_id = 1  # Start at the root directory

    def _get_connection(self):
        return sqlite3.connect(DATABASE_PATH)

    def pwd(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        path = []
        dir_id = self.current_dir_id
        while dir_id is not None:
            cursor.execute('SELECT name, pid FROM directories WHERE id = ?', (dir_id,))
            result = cursor.fetchone()
            if result:
                dir_name, parent_id = result
                if dir_name != "/":
                    path.insert(0, dir_name)
                dir_id = parent_id
            else:
                break

        conn.close()
        
        return '/' if not path else '/' + '/'.join(path)

    def rm(self, path):
        """Removes a file or directory, with support for full paths and recursive directory deletion."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Split the path into directories and the target file/directory
        directories, target_name = os.path.split(path)
        
        # Get the parent directory ID
        try:
            parent_dir_id = self._get_directory_id(directories) if directories else self.current_dir_id
        except FileNotFoundError:
            conn.close()
            raise FileNotFoundError(f"rm: cannot remove '{path}': No such file or directory")

        # Check if it's a directory
        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (parent_dir_id, target_name))
        dir_result = cursor.fetchone()

        if dir_result:
            # Recursively delete the contents if it's a directory
            dir_id = dir_result[0]

            # Check if the directory is empty
            cursor.execute('SELECT COUNT(*) FROM directories WHERE pid = ?', (dir_id,))
            subdir_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM files WHERE pid = ?', (dir_id,))
            file_count = cursor.fetchone()[0]

            if subdir_count > 0 or file_count > 0:
                # Directory is not empty; recursively delete
                self._recursive_remove_directory(dir_id)

            # Remove the directory itself
            cursor.execute('DELETE FROM directories WHERE id = ?', (dir_id,))
            conn.commit()
            conn.close()
            return f"Directory '{path}' removed (and contents, if any)."

        # Check if it's a file
        cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (parent_dir_id, target_name))
        file_result = cursor.fetchone()

        if file_result:
            # Remove the file
            cursor.execute('DELETE FROM files WHERE id = ?', (file_result[0],))
            conn.commit()
            conn.close()
            return f"File '{path}' removed."

        conn.close()
        raise FileNotFoundError(f"rm: cannot remove '{path}': No such file or directory")

    def _recursive_remove_directory(self, dir_id):
        """Helper method to recursively delete a directory's contents."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Recursively remove all subdirectories
        cursor.execute('SELECT id FROM directories WHERE pid = ?', (dir_id,))
        subdirs = cursor.fetchall()
        for subdir in subdirs:
            self._recursive_remove_directory(subdir[0])

        # Remove all files in the directory
        cursor.execute('DELETE FROM files WHERE pid = ?', (dir_id,))
        conn.commit()

        # Remove the directory itself
        cursor.execute('DELETE FROM directories WHERE id = ?', (dir_id,))
        conn.commit()

        conn.close()

    def ls(self, flags=[]):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT name FROM directories WHERE pid = ?', (self.current_dir_id,))
        subdirs = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT name FROM files WHERE pid = ?', (self.current_dir_id,))
        files = [row[0] for row in cursor.fetchall()]

        files_and_dirs = subdirs + files

        if '-a' not in flags:
            files_and_dirs = [item for item in files_and_dirs if not item.startswith('.')]

        conn.close()
        return files_and_dirs

    def mkdir(self, dir_name):
        """Creates a new directory."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (self.current_dir_id, dir_name))
        if cursor.fetchone():
            conn.close()
            raise Exception(f"mkdir: cannot create directory '{dir_name}': Directory exists")

        cursor.execute('''
            INSERT INTO directories (pid, oid, name, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.current_dir_id, 1, dir_name, datetime.now(), datetime.now()))

        conn.commit()
        conn.close()
        return f"Directory '{dir_name}' created."


    def touch(self, file_name):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        if cursor.fetchone():
            conn.close()
            raise Exception(f"touch: cannot create file '{file_name}': File exists")

        cursor.execute('''
            INSERT INTO files (pid, oid, name, creation_date, modified_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.current_dir_id, 1, file_name, datetime.now(), datetime.now()))

        conn.commit()
        conn.close()
        return f"File '{file_name}' created."

    def cd(self, path):
        conn = self._get_connection()
        cursor = conn.cursor()

        path = path.rstrip("/")
        
        if os.path.isabs(path):  # Absolute path, start from root
            components = path.strip("/").split("/")
            current_dir_id = 1  # Start from root directory
        else:  # Relative path, start from current directory
            components = path.split("/")
            current_dir_id = self.current_dir_id

        for component in components:
            if component == "..":
                cursor.execute('SELECT pid FROM directories WHERE id = ?', (current_dir_id,))
                result = cursor.fetchone()
                if result and result[0] is not None:
                    current_dir_id = result[0]
                else:
                    raise Exception("cd: already at the root directory.")
            elif component == "." or component == "":
                continue
            else:
                cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, component))
                result = cursor.fetchone()
                if result:
                    current_dir_id = result[0]
                else:
                    raise Exception(f"cd: no such directory: {component}")

        self.current_dir_id = current_dir_id
        conn.close()

    def cat(self, file_names, flags=[], output_file=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        all_contents = []
        for file_name in file_names:
            cursor.execute('SELECT contents FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
            file_data = cursor.fetchone()

            if not file_data:
                conn.close()
                raise Exception(f"cat: {file_name}: No such file or directory")
            
            file_content = file_data[0].rstrip()  # Remove trailing newlines or spaces
            all_contents.append(file_content)

        conn.close()

        combined_content = ' '.join(all_contents)

        processed_content = self._apply_cat_flags(combined_content, flags)

        if output_file:
            self._write_to_file(output_file, processed_content)
            return f"Concatenated content saved to {output_file} with size {len(processed_content)} bytes."

        return processed_content

    def _apply_cat_flags(self, content, flags):
        lines = content.splitlines()  # Split into lines for easier processing
        result = []
        line_number = 1

        for i, line in enumerate(lines):
            if '-s' in flags and line == "" and (i > 0 and lines[i - 1] == ""):
                continue

            if '-n' in flags:
                result.append(f"{line_number}  {line}")
                line_number += 1
            elif '-b' in flags:
                if line.strip() != "":
                    result.append(f"{line_number}  {line}")
                    line_number += 1
                else:
                    result.append(line)
            else:
                result.append(line)

            if '-E' in flags:
                result[-1] += "$"

        if '-T' in flags:
            result = [line.replace("\t", "^I") for line in result]

        return "\n".join(result)

    def _write_to_file(self, file_name, content):
        conn = self._get_connection()
        cursor = conn.cursor()

        new_size = len(content)

        cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        file_data = cursor.fetchone()

        if file_data:
            cursor.execute('''
                UPDATE files 
                SET contents = ?, size = ?, modified_date = ? 
                WHERE id = ?
            ''', (content, new_size, datetime.now(), file_data[0]))
        else:
            cursor.execute('''
                INSERT INTO files (pid, oid, name, contents, size, creation_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_dir_id, 1, file_name, content, new_size, datetime.now(), datetime.now()))

        conn.commit()
        conn.close()

    def edit_and_save_file(self, file_name, new_contents=None):
        """Open a file to view its current contents and allow editing on top of the existing content."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Fetch the file's current contents
        cursor.execute('SELECT contents FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        file_data = cursor.fetchone()

        if not file_data:
            conn.close()
            raise Exception(f"nano: {file_name}: No such file or directory")

        current_contents = file_data[0]

        # If no new content is provided, just return the current file contents for editing
        if new_contents is None:
            conn.close()
            return {"file_contents": current_contents}

        # If new contents are provided, append them to the existing contents
        updated_contents = current_contents + new_contents

        new_size = len(updated_contents)

        # Update the file with the new content and size
        cursor.execute('''
            UPDATE files
            SET contents = ?, size = ?, modified_date = ?
            WHERE pid = ? AND name = ?
        ''', (updated_contents, new_size, datetime.now(), self.current_dir_id, file_name))

        if cursor.rowcount == 0:
            conn.close()
            raise Exception(f"nano: {file_name}: No such file or directory")

        conn.commit()
        conn.close()

        return f"File '{file_name}' updated successfully with size {new_size} bytes."

    def _get_directory_id(self, directory_path):
        """Helper method to get the directory ID based on a directory path (e.g., 'Assignments/MyDocs')."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Split the directory path into components
        directories = directory_path.split("/")
        current_dir_id = self.current_dir_id

        for dir_name in directories:
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, dir_name))
            directory = cursor.fetchone()

            if not directory:
                conn.close()
                raise FileNotFoundError(f"Directory '{directory_path}' not found")

            current_dir_id = directory[0]  # Update to the next directory ID

        conn.close()
        return current_dir_id

    def copy_file(self, source_path, destination_path, user_id=1, preserve_attributes=False, verbose=False):
        """Copies a file from source path to destination path. Handles full paths for both source and destination."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Split the source and destination paths into directories and file names
        source_dirs, source_file_name = os.path.split(source_path)
        destination_dirs, destination_file_name = os.path.split(destination_path)

        # Get the source directory ID (handle full path)
        source_dir_id = self._get_directory_id(source_dirs)

        # Get the destination directory ID (handle full path, create if it doesn't exist)
        try:
            destination_dir_id = self._get_directory_id(destination_dirs)
        except FileNotFoundError:
            self.mkdir(destination_dirs)
            destination_dir_id = self._get_directory_id(destination_dirs)

        # Check if the source file exists in the source directory
        cursor.execute('SELECT * FROM files WHERE pid = ? AND name = ?', (source_dir_id, source_file_name))
        source_file = cursor.fetchone()

        if not source_file:
            raise FileNotFoundError(f"cp: cannot stat '{source_file_name}': No such file in '{source_dirs}'")

        # Copy the file contents
        contents = source_file[7]  # Assuming contents are in the 7th column
        if preserve_attributes:
            creation_date = source_file[5]
            modified_date = source_file[6]
        else:
            creation_date = datetime.now()
            modified_date = datetime.now()

        # Check if the destination file already exists
        cursor.execute('SELECT * FROM files WHERE pid = ? AND name = ?', (destination_dir_id, destination_file_name))
        dest_file = cursor.fetchone()

        if dest_file:
            cursor.execute('''
                UPDATE files 
                SET contents = ?, creation_date = ?, modified_date = ?
                WHERE pid = ? AND name = ?
            ''', (contents, creation_date, modified_date, destination_dir_id, destination_file_name))
        else:
            cursor.execute('''
                INSERT INTO files (pid, oid, name, contents, creation_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (destination_dir_id, user_id, destination_file_name, contents, creation_date, modified_date))

        conn.commit()
        conn.close()

        return f"File '{source_file_name}' copied from '{source_dirs}' to '{destination_path}'"

    def copy_directory(self, source_dir, destination_dir, user_id=1, preserve_attributes=False, verbose=False):
        """Copies a directory recursively from source to destination."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get the source directory ID (handle full path)
        source_dir_id = self._get_directory_id(source_dir)

        # Get destination directory ID (create if it doesn't exist)
        try:
            destination_dir_id = self._get_directory_id(destination_dir)
        except FileNotFoundError:
            self.mkdir(destination_dir)
            destination_dir_id = self._get_directory_id(destination_dir)

        # Recursively copy the files in the directory
        cursor.execute('SELECT * FROM files WHERE pid = ?', (source_dir_id,))
        files_in_directory = cursor.fetchall()

        for file in files_in_directory:
            source_file_name = file[3]  # Assuming the 3rd index is the file name
            self.copy_file(os.path.join(source_dir, source_file_name), os.path.join(destination_dir, source_file_name), user_id, preserve_attributes, verbose)

        # Recursively copy subdirectories
        cursor.execute('SELECT * FROM directories WHERE pid = ?', (source_dir_id,))
        subdirs = cursor.fetchall()

        for subdir in subdirs:
            subdir_name = subdir[3]  # Assuming the 3rd index is the directory name
            self.copy_directory(os.path.join(source_dir, subdir_name), os.path.join(destination_dir, subdir_name), user_id, preserve_attributes, verbose)

        conn.close()

        return f"Directory '{source_dir}' copied to '{destination_dir}'"
    
    def mv(self, source_path, destination_path, user_id=1):
        """Move a file or directory from source to destination, creating destination folder if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get the source directory ID and the final source file or directory name
        source_dirs, source_name = os.path.split(source_path)
        
        source_dir_id = self._get_directory_id(source_dirs)
        
        

        # Get the destination directory ID and final destination file or directory name
        destination_dirs, destination_name = os.path.split(destination_path)

        # If destination is just a directory (without a filename), use the source name as the destination name
        if not destination_name:
            destination_name = source_name

        # Check if the destination directory exists, if not, create it
        try:
            destination_dir_id = self._get_directory_id(destination_dirs)
        except FileNotFoundError:
            self._create_directory_chain(destination_dirs)  # Create the destination directory and any parent directories
            destination_dir_id = self._get_directory_id(destination_dirs)

        # Check if it's a directory
        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (source_dir_id, source_name))
        dir_result = cursor.fetchone()

        if dir_result:
            # Move the entire directory recursively
            self._move_directory(dir_result[0], destination_dir_id, destination_name)
            conn.commit()
            conn.close()
            return f"Directory '{source_path}' moved to '{destination_path}'"

        # Check if it's a file
        cursor.execute('SELECT * FROM files WHERE pid = ? AND name = ?', (source_dir_id, source_name))
        file_result = cursor.fetchone()

        if file_result:
            # Check if the destination file already exists
            cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (destination_dir_id, destination_name))
            dest_file = cursor.fetchone()

            # Overwrite the destination file if it exists
            if dest_file:
                cursor.execute('''
                    UPDATE files
                    SET contents = ?, modified_date = ?
                    WHERE id = ?
                ''', (file_result[7], datetime.now(), dest_file[0]))
            else:
                # Move the file (create new entry at the destination)
                cursor.execute('''
                    INSERT INTO files (pid, oid, name, contents, creation_date, modified_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (destination_dir_id, user_id, destination_name, file_result[7], file_result[5], datetime.now()))

            # Remove the source file after moving
            cursor.execute('DELETE FROM files WHERE id = ?', (file_result[0],))
            conn.commit()
            conn.close()
            return f"File '{source_path}' moved to '{destination_path}'"

        conn.close()
        raise FileNotFoundError(f"mv: cannot stat '{source_path}': No such file or directory")

    def _create_directory_chain(self, directory_path):
        """Helper function to create a directory and its parent directories if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        directories = directory_path.split("/")
        current_dir_id = self.current_dir_id

        for directory in directories:
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, directory))
            result = cursor.fetchone()

            if not result:
                # Create the directory if it doesn't exist
                cursor.execute('''
                    INSERT INTO directories (pid, oid, name, created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (current_dir_id, 1, directory, datetime.now(), datetime.now()))
                current_dir_id = cursor.lastrowid
            else:
                current_dir_id = result[0]  # Move into the next directory

        conn.commit()
        conn.close()