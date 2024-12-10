import sqlite3
from datetime import datetime
import os  # For handling paths
from typing import List
import pdb 


DATABASE_PATH = 'filesystem.sqlite'

class FileSystem:
    def __init__(self):
        self.current_dir_id = 1  # Start at the root directory
        self.current_user_id=1  #start with root user

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

    def rm(self, path: str, recursive: bool = False):
        """
        Removes a file or directory, supporting recursive deletion for directories.
        """
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
            if recursive:
                dir_id = dir_result[0]
                self._recursive_remove_directory(dir_id)
                # Remove the directory itself
                cursor.execute('DELETE FROM directories WHERE id = ?', (dir_id,))
                conn.commit()
                conn.close()
                return f"Directory '{path}' removed (and contents, if any)."
            else:
                conn.close()
                raise IsADirectoryError(f"rm: cannot remove '{path}': Is a directory")
        
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

    def _recursive_remove_directory(self, dir_id: int):
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
        """
        List the contents of the current directory with optional flags.
        - Supports:
            - `-a`: Show hidden files (starting with .)
            - `-l`: Long format listing (permissions, owner, size, modified time)
            - `-h`: Human-readable file sizes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Fetch directories and files in the current directory
        cursor.execute('SELECT name, oid, created_at, modified_at, read_permission, write_permission, execute_permission FROM directories WHERE pid = ?', (self.current_dir_id,))
        subdirs = cursor.fetchall()

        cursor.execute('SELECT name, oid, size, creation_date, modified_date, read_permission, write_permission, execute_permission FROM files WHERE pid = ?', (self.current_dir_id,))
        files = cursor.fetchall()

        # Handle flags
        show_hidden = '-a' in flags
        long_listing = '-l' in flags
        human_readable = '-h' in flags

        # Prepare the output list
        output = []

        # Combine directories and files into one list
        items = [("d", name, oid, None, created_at, modified_at, r, w, x) for (name, oid, created_at, modified_at, r, w, x) in subdirs]
        items += [("f", name, oid, size, creation_date, modified_date, r, w, x) for (name, oid, size, creation_date, modified_date, r, w, x) in files]

        for item_type, name, oid, size, created_at, modified_date, read_perm, write_perm, exec_perm in items:
            if not show_hidden and name.startswith('.'):
                continue

            line = []

            # Long format listing
            if long_listing:
                permissions = self._get_permissions(item_type, read_perm, write_perm, exec_perm)  # Updated to fetch actual permissions
                line.append(permissions)
                line.append(f"{oid}\t")  # Owner ID
                if item_type == "f" and human_readable:
                    line.append(f"{self._human_readable(size)}\t")
                else:
                    line.append(f"{size if size else ''}\t")
                
                # Print created and modified dates for files and directories
                line.append(f"{created_at.split('.')[0]}\t")  # Strip the microseconds
                line.append(f"{modified_date.split('.')[0] if modified_date else ''}\t")  # Strip the microseconds

            # Add file/directory name
            line.append(f"{name}\n")

            output.append(''.join(line))

        conn.close()
        return ''.join(output)


    def _get_permissions(self, item_type, read_perm, write_perm, exec_perm):
        """
        Helper function to get the permission string for directories and files.
        """
        perm_str = ""
        if item_type == "d":
            perm_str += 'd'  # Directory
        else:
            perm_str += '-'  # File

        # User permissions
        perm_str += 'r' if read_perm else '-'
        perm_str += 'w' if write_perm else '-'
        perm_str += 'x' if exec_perm else '-'

        # Group permissions (assuming you have logic to define group permissions)
        perm_str += 'r' if read_perm else '-'
        perm_str += 'w' if write_perm else '-'
        perm_str += 'x' if exec_perm else '-'

        # World permissions (assuming same as user for simplicity)
        perm_str += 'r' if read_perm else '-'
        perm_str += 'w' if write_perm else '-'
        perm_str += 'x' if exec_perm else '-'

        return perm_str



    def _human_readable(self, size):
        """
        Helper function to convert bytes to a human-readable format (KB, MB, GB, etc.).
        """
        units = ['B', 'K', 'M', 'G', 'T', 'P']
        for unit in units:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}P"

    def mkdir(self, path: str):
        """
        Creates a new directory, including necessary parent directories if not existing.
        Path handling is done within the virtual filesystem without using the host OS.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Split the path into components
        directories = path.strip("/").split("/")
        current_dir_id = self.current_dir_id  # Use the current directory ID as the base

        for i, dir_name in enumerate(directories):
            # Check if the directory exists in the current directory ID
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, dir_name))
            directory = cursor.fetchone()

            if not directory:
                # If parent directory in the path doesn't exist, raise an error
                if i < len(directories) - 1:
                    conn.close()
                    raise Exception(f"mkdir: {dir_name}: No such file or directory")

                # Create the directory if it's the final part of the path
                cursor.execute('''
                    INSERT INTO directories (pid, oid, name, created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (current_dir_id, 1, dir_name, datetime.now(), datetime.now()))
                current_dir_id = cursor.lastrowid  # Update to the newly created directory ID
            else:
                current_dir_id = directory[0]  # Move into the existing directory

        conn.commit()
        conn.close()

        return f"Directory '{path}' created."
    
    def get_current_user(self):
        """Fetch the current user ID from the users table."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Fetch the user ID based on the current_user_id stored in the FileSystem instance
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (self.current_user_id,))
        result = cursor.fetchone()

        conn.close()

        if result:
            return result[0]  # Return the user ID
        else:
            raise Exception("User not found")




    def touch(self, file_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        print("file name is", file_name)
        # Check if the file already exists in the current directory
        cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        if cursor.fetchone():
            conn.close()
            raise Exception(f"touch: cannot create file '{file_name}': File exists")

        # Insert the new file record into the 'files' table
        cursor.execute('''
            INSERT INTO files (pid, oid, name, creation_date, modified_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.current_dir_id, self.get_current_user(), file_name, datetime.now(), datetime.now()))

        conn.commit()
        conn.close()
        return f"File '{file_name}' created."

    def cd(self, path):
        """
        Changes the current working directory within the virtual filesystem.
        Supports absolute, relative paths, and '~' for the home directory.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Remove trailing slashes from the path
        path = path.rstrip("/")

        # Handle '~' as the root directory ('root' directory with id=1 and pid=NULL)
        if path == "~":
            self.current_dir_id = 1  # Set the current directory to the root directory (id=1)
            conn.close()
            print("THis line was hit")
            return f"Changed to directory '/root'"

        # If the path is absolute, start from the root directory
        if os.path.isabs(path):
            components = path.strip("/").split("/")
            current_dir_id = 1  # Root directory ID is 1
        else:  # If the path is relative, start from the current directory
            components = path.split("/")
            current_dir_id = self.current_dir_id

        for component in components:
            if component == "..":  # Navigate to the parent directory
                cursor.execute('SELECT pid FROM directories WHERE id = ?', (current_dir_id,))
                result = cursor.fetchone()
                if result and result[0] is not None:
                    current_dir_id = result[0]
                else:
                    conn.close()
                    raise Exception("cd: already at the root directory.")
            elif component == "." or component == "":  # Stay in the current directory
                continue
            else:  # Navigate into the subdirectory
                cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, component))
                result = cursor.fetchone()
                if result:
                    current_dir_id = result[0]
                else:
                    conn.close()
                    raise Exception(f"cd: no such directory: {component}")

        # Update the current directory ID to the new directory
        self.current_dir_id = current_dir_id
        conn.close()

        # Return the current directory path
        return f"Changed to directory '{self.pwd()}'"



    def cat(self, file_names: List[str]):
        """Concatenates the contents of one or more files."""
        conn = self._get_connection()
        cursor = conn.cursor()

        all_contents = []
        for file_name in file_names:
            cursor.execute('SELECT contents FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
            file_data = cursor.fetchone()

            if not file_data:
                conn.close()
                raise FileNotFoundError(f"cat: {file_name}: No such file or directory")
            
            file_content = file_data[0]  # File contents are stored in the BLOB column
            all_contents.append(file_content)

        conn.close()

        # Join the contents of all files and return as a single string
        return ''.join(all_contents)


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

    def _get_directory_id(self, absolute_path: str):
        """
        Retrieves the directory ID based on an absolute path.
        Supports only absolute paths, starting from the root directory.
        """
        # Ensure the path starts with "/"
        if not absolute_path.startswith("/"):
            raise ValueError("Only absolute paths are supported.")
        
        #pdb.set_trace()  # Start debugging here

        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Start from the root directory
        cursor.execute('SELECT id FROM directories WHERE pid IS NULL AND name = "root"')
        root_dir = cursor.fetchone()
        if not root_dir:
            conn.close()
            raise FileNotFoundError("Root directory not found.")
        
        current_dir_id = root_dir[0]

        # Remove leading/trailing slashes and split the path
        directories = absolute_path.strip("/").split("/")
        print("\n files in directories\n", directories)

        # Traverse each directory in the path
        for dir_name in directories:
            if not dir_name or dir_name=='root':  # Skip any empty segments
                continue

            # Query for the next directory in the path
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, dir_name))
            directory = cursor.fetchone()
            
            if not directory:
                conn.close()
                raise FileNotFoundError(f"Directory '{dir_name}' not found in path '{absolute_path}'")
            
            current_dir_id = directory[0]  # Move to the next directory in the path

        conn.close()
        return current_dir_id






    def _create_directory_chain(self, directory_path: str) -> int:
        """
        Helper function to create directories in a given path if they do not exist.
        Returns the ID of the final directory in the chain.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        directories = directory_path.strip("/").split("/")
        current_dir_id = self.current_dir_id  # Start from the current directory

        for directory in directories:
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (current_dir_id, directory))
            result = cursor.fetchone()
            if not result:
                # Create the directory if it doesn't exist
                cursor.execute('''
                    INSERT INTO directories (pid, oid, name, created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (current_dir_id, self.current_user_id, directory, datetime.now(), datetime.now()))
                current_dir_id = cursor.lastrowid
            else:
                current_dir_id = result[0]  # Move into the next existing directory

        conn.commit()
        conn.close()
        return current_dir_id

    def copy_File_Directory(self, source: str, destination: str, is_directory: bool):
        """
        Copies a file or directory from source to destination.
        Handles both absolute and relative paths, including creating the destination
        directory if it does not exist.
        """
        print("\nCopy function started. Source:", source, "Destination:", destination)

        # Resolve source path
        if source.startswith("/"):
            source_dir_id = self._get_directory_id(os.path.dirname(source))
            source_item = os.path.basename(source)
        else:
            source_path = self.pwd() + "/" + source
            source_dir_id = self._get_directory_id(os.path.dirname(source_path))
            source_item = os.path.basename(source)

        # Resolve destination path
        if destination.startswith("/"):
            destination_dir_path = destination if destination.endswith("/") else os.path.dirname(destination)
            destination_dir_id = self._get_directory_id(destination_dir_path)  # Create dir if it doesn't exist
            destination_item = os.path.basename(destination) or source_item
        else:
            destination_path = self.pwd() + "/" + destination
            destination_dir_id = self._get_directory_id(os.path.dirname(destination_path))  # Create dir if it doesn't exist
            destination_item = os.path.basename(destination) or source_item

        conn = self._get_connection()
        cursor = conn.cursor()

        # Perform the copy based on whether it's a directory or a file
        if is_directory:
            # Use recursive directory copy if it's a directory
            result = self._copy_directory_recursive(source_dir_id, destination_dir_id, cursor, source_item, destination_item)
            conn.commit()
            conn.close()
            return result

        else:
            # Handle file copy
            cursor.execute('SELECT * FROM files WHERE pid = ? AND name = ?', (source_dir_id, source_item))
            file_result = cursor.fetchone()

            if not file_result:
                raise FileNotFoundError(f"File '{source}' not found.")

            source_file_name = destination_item
            file_contents = file_result[7]
            creation_date = datetime.now()
            modified_date = datetime.now()

            # Check if the destination file already exists
            cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (destination_dir_id, source_file_name))
            existing_file = cursor.fetchone()

            if existing_file:
                # If the file already exists, update its contents
                cursor.execute('''
                    UPDATE files 
                    SET contents = ?, modified_date = ?
                    WHERE id = ?
                ''', (file_contents, modified_date, existing_file[0]))
            else:
                # Otherwise, insert a new file
                cursor.execute('''
                    INSERT INTO files (pid, oid, name, contents, creation_date, modified_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (destination_dir_id, self.current_user_id, source_file_name, file_contents, creation_date, modified_date))

            conn.commit()
            conn.close()
            return f"File '{source}' copied to '{destination}'."



    def _copy_directory_recursive(self, source_dir_id, destination_dir_id, cursor, source_item, destination_item):
        """
        Recursively copy a directory and its contents to the destination.
        """
        # Check if the destination subdirectory already exists
        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (destination_dir_id, destination_item))
        existing_dir = cursor.fetchone()

        if existing_dir:
            new_destination_dir_id = existing_dir[0]  # Use the existing directory ID
        else:
            # Create the destination subdirectory if it doesn't exist
            cursor.execute('''
                INSERT INTO directories (pid, oid, name, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (destination_dir_id, self.current_user_id, destination_item, datetime.now(), datetime.now()))
            new_destination_dir_id = cursor.lastrowid

        # Copy all subdirectories recursively
        cursor.execute('SELECT * FROM directories WHERE pid = ? AND name = ?', (source_dir_id, source_item))
        subdirs = cursor.fetchall()

        for subdir in subdirs:
            subdir_name = subdir[3]  # Assuming name is in the 3rd column
            self._copy_directory_recursive(subdir[0], new_destination_dir_id, cursor, subdir_name, subdir_name)

        # Copy all files in the directory
        cursor.execute('SELECT * FROM files WHERE pid = ?', (source_dir_id,))
        files = cursor.fetchall()

        for file in files:
            file_name = file[3]  # Assuming name is in the 3rd column
            file_contents = file[7]  # Assuming contents are in the 7th column
            creation_date = datetime.now()
            modified_date = datetime.now()

            # Insert each file into the new destination directory
            cursor.execute('''
                INSERT INTO files (pid, oid, name, contents, creation_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (new_destination_dir_id, self.current_user_id, file_name, file_contents, creation_date, modified_date))

        return f"Directory '{source_item}' copied to '{destination_item}' in destination."




    
    def mv(self, source: str, destination: str, is_directory: bool):
        """
        Moves a file or directory from source to destination.
        Handles both absolute and relative paths.
        """
        print("\nMove function started. Source:", source, "Destination:", destination)

        # Resolve source path
        if source.startswith("/"):
            source_dir_id = self._get_directory_id(os.path.dirname(source))
            source_item = os.path.basename(source)
        else:
            source_path = self.pwd() + "/" + source
            source_dir_id = self._get_directory_id(os.path.dirname(source_path))
            source_item = os.path.basename(source)

        # Check destination path
        if destination.startswith("/"):
            destination_dir_id = self._get_directory_id(destination) if destination.endswith("/") else self._get_directory_id(os.path.dirname(destination))
            destination_item = os.path.basename(destination) if not destination.endswith("/") else source_item
        else:
            destination_path = self.pwd() + "/" + destination
            destination_dir_id = self._get_directory_id(destination_path) if destination.endswith("/") else self._get_directory_id(os.path.dirname(destination_path))
            destination_item = os.path.basename(destination) if not destination.endswith("/") else source_item

        # Check if destination is a directory
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (destination_dir_id, destination_item))
        destination_exists = cursor.fetchone()

        if destination_exists:  # If destination is a directory, move into it
            final_destination_id = destination_exists[0]
            new_name = source_item  # Retain original name inside destination directory
        else:
            # Otherwise, treat the destination as a file name or directory
            final_destination_id = destination_dir_id
            new_name = destination_item  # Use the specified destination name

        if is_directory:
            # Move directory by updating its parent directory (`pid`)
            cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (source_dir_id, source_item))
            dir_result = cursor.fetchone()
            if dir_result:
                cursor.execute('''
                    UPDATE directories
                    SET pid = ?, name = ?
                    WHERE id = ?
                ''', (final_destination_id, new_name, dir_result[0]))
                conn.commit()
                conn.close()
                return f"Directory '{source}' moved to '{destination}'"
            else:
                conn.close()
                raise FileNotFoundError(f"Directory '{source}' not found.")
        else:
            # Move file by updating its parent directory (`pid`)
            cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (source_dir_id, source_item))
            file_result = cursor.fetchone()
            if file_result:
                cursor.execute('''
                    UPDATE files
                    SET pid = ?, name = ?
                    WHERE id = ?
                ''', (final_destination_id, new_name, file_result[0]))
                conn.commit()
                conn.close()
                return f"File '{source}' moved to '{destination}'"
            else:
                conn.close()
                raise FileNotFoundError(f"File '{source}' not found.")









        
    def tail(self, file_name: str, num_lines: int = 10) -> str:
        """
        Return the last `num_lines` lines of the specified file in the virtual filesystem.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if the file exists in the current directory
        cursor.execute('SELECT contents FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        file_data = cursor.fetchone()

        if not file_data:
            conn.close()
            raise FileNotFoundError(f"File '{file_name}' not found")

        file_content = file_data[0].splitlines()  # Split file contents into lines
        last_n_lines = file_content[-num_lines:]  # Get the last N lines
        result = '\n'.join(last_n_lines)  # Join lines back into a string

        conn.close()
        return result
    
    
    def head(self, file_name: str, num_lines: int = 10) -> str:
        """
        Fetches the first `num_lines` lines of a file.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if the file exists
        cursor.execute('SELECT contents FROM files WHERE pid = ? AND name = ?', (self.current_dir_id, file_name))
        file_data = cursor.fetchone()

        if not file_data:
            conn.close()
            raise FileNotFoundError(f"head: cannot access '{file_name}': No such file or directory")

        file_contents = file_data[0].splitlines()  # Split contents into lines
        result = "\n".join(file_contents[:num_lines])  # Get the first `num_lines` lines

        conn.close()
        return result

    def chmod(self, path: str, permissions: int):
        """Change the permissions of a file or directory."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get the directory and file names
        directory, file_name = os.path.split(path)

        # Get the parent directory ID
        try:
            parent_dir_id = self._get_directory_id(directory)
        except FileNotFoundError:
            conn.close()
            raise FileNotFoundError(f"chmod: cannot access '{path}': No such file or directory")

        # Check if it's a directory
        cursor.execute('SELECT id FROM directories WHERE pid = ? AND name = ?', (parent_dir_id, file_name))
        dir_result = cursor.fetchone()

        if dir_result:
            # Update the directory permissions
            cursor.execute('UPDATE directories SET read_permission=?, write_permission=?, execute_permission=? WHERE id=?',
                        (permissions & 0o400 != 0, permissions & 0o200 != 0, permissions & 0o100 != 0, dir_result[0]))
            conn.commit()
            conn.close()
            return f"Permissions of directory '{path}' changed."

        # Check if it's a file
        cursor.execute('SELECT id FROM files WHERE pid = ? AND name = ?', (parent_dir_id, file_name))
        file_result = cursor.fetchone()

        if file_result:
            # Update the file permissions
            cursor.execute('UPDATE files SET read_permission=?, write_permission=?, execute_permission=? WHERE id=?',
                        (permissions & 0o400 != 0, permissions & 0o200 != 0, permissions & 0o100 != 0, file_result[0]))
            conn.commit()
            conn.close()
            return f"Permissions of file '{path}' changed."

        conn.close()
        raise FileNotFoundError(f"chmod: cannot access '{path}': No such file or directory")