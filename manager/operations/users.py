import sqlite3
import logging
from manager.utils import DB_PATH, DatabaseError, UserRole, log_action
from manager.utils import db_error_handler

@db_error_handler
def add_user(user_id: str, name: str, role: str) -> None:
    """Add a new user to the database."""
    try:
        # Validate role
        try:
            role_enum = UserRole(role)
        except ValueError:
            raise ValueError(f"Invalid role: {role}. Must be one of {[r.value for r in UserRole]}")

        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            
            # Check if user exists
            cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                raise DatabaseError(f"User {user_id} already exists.")

            cursor.execute("""
                INSERT INTO Users (user_id, name, role)
                VALUES (?, ?, ?)
            """, (user_id, name, role_enum.value))
            
            connection.commit()
            
        log_action('Users', user_id, 'creation', 'system')
        logging.info(f"User '{name}' added successfully.")
            
    except Exception as e:
        logging.error(f"Failed to add user: {str(e)}")
        raise
