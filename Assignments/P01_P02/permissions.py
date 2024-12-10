import sqlite3
from database import DATABASE_PATH

class Permissions:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

    def user_has_permission(self, file_id, dir_id, user_id, permission_type):
        """Check if a user has the specified permission for a file or directory."""
        self.cursor.execute('''
            SELECT read_permission, write_permission, execute_permission 
            FROM permissions 
            WHERE (file_id = ? OR dir_id = ?) AND user_id = ?
        ''', (file_id, dir_id, user_id))
        permissions = self.cursor.fetchone()

        if permissions:
            if permission_type == 'read' and permissions[0]:
                return True
            if permission_type == 'write' and permissions[1]:
                return True
            if permission_type == 'execute' and permissions[2]:
                return True
        
        return False

    def set_permissions(self, file_id, dir_id, user_id, read, write, execute, authenticated_user_id):
        """Only the authenticated user with proper permissions can set permissions."""
        if not self.user_has_permission(file_id, dir_id, authenticated_user_id, 'write'):
            return {"error": "User does not have write permission to set permissions for this file/directory."}

        # Proceed to set permissions after verification
        self.cursor.execute('''
            INSERT INTO permissions (file_id, dir_id, user_id, read_permission, write_permission, execute_permission)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_id, dir_id, user_id, read, write, execute))
        self.conn.commit()
        return {"message": f"Permissions set for file/directory {file_id or dir_id} and user {user_id}."}

    def get_permissions(self, file_id, dir_id, user_id):
        """Get permissions for a specific file or directory and user."""
        self.cursor.execute('''
            SELECT read_permission, write_permission, execute_permission
            FROM permissions
            WHERE (file_id = ? OR dir_id = ?) AND user_id = ?
        ''', (file_id, dir_id, user_id))
        permissions = self.cursor.fetchone()

        if permissions:
            return {
                "read_permission": permissions[0],
                "write_permission": permissions[1],
                "execute_permission": permissions[2]
            }
        else:
            return {"error": f"No permissions found for file/directory {file_id or dir_id} and user {user_id}."}

    def close(self):
        """Close the database connection."""
        self.conn.close()
