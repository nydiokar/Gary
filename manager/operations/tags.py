import sqlite3
import logging
from utils import DB_PATH, DatabaseError, log_action, db_error_handler

@db_error_handler
def add_tag(name: str) -> int:
    """Add a new tag to the database."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            
            # Check if tag exists
            cursor.execute("SELECT name FROM Tags WHERE name = ?", (name,))
            if cursor.fetchone():
                raise DatabaseError(f"Tag '{name}' already exists.")

            cursor.execute("INSERT INTO Tags (name) VALUES (?)", (name,))
            tag_id = cursor.lastrowid
            connection.commit()
            
        log_action('Tags', str(tag_id), 'creation', 'system')
        logging.info(f"Tag '{name}' added successfully.")
        return tag_id
            
    except Exception as e:
        logging.error(f"Failed to add tag: {str(e)}")
        raise