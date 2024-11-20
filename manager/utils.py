import sqlite3
import logging
from enum import Enum
from typing import List, Tuple, Callable
import re
import datetime
from datetime import timedelta

# Constants and configurations
DB_PATH = "nesha_task_manager.db"
SYSTEM_USER_ID = "system"

class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass

class UserRole(Enum):
    MANAGER = "Manager"
    EXPERT = "Expert"
    USER = "User"
    SYSTEM = "system"

class TaskStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REFUSED = "Refused"
    COMPLETED = "Completed"
    VERIFIED = "Verified"

def check_existing_tables() -> List[Tuple[str]]:
    """Check for existing tables in the database."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return cursor.fetchall()

def log_action(entity: str, entity_id: str, action: str, performed_by: str) -> None:
    """Log database changes to AuditLogs."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO AuditLogs (entity, entity_id, action, performed_by)
                VALUES (?, ?, ?, ?)
            """, (entity, entity_id, action, performed_by))
            connection.commit()
    except Exception as e:
        logging.error(f"Failed to log action: {str(e)}")
        raise

def assign_tag_to_task(task_id: str, tag_id: int):
    """Assign a tag to a task."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO TaskTags (task_id, tag_id) VALUES (?, ?)", (task_id, tag_id))
            connection.commit()
        log_action('TaskTags', f'{task_id}:{tag_id}', 'tag_assignment', SYSTEM_USER_ID)
    except Exception as e:
        logging.error(f"Failed to assign tag: {e}")
        raise

def log_recurring_task_action(recurring_task_id: str, action: str) -> None:
    """Log actions related to recurring tasks."""
    log_action('RecurringTasks', recurring_task_id, action, 'system')

def log_task_action(task_id: str, action: str) -> None:
    """Log actions related to tasks."""
    log_action('Tasks', task_id, action, 'system')

def db_error_handler(func: Callable):
    """Decorator to handle database-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logging.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"{func.__name__} failed due to a database error.")
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper   


