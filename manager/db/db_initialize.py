import sqlite3
import logging
from datetime import datetime
from operations.tags import add_tag
from operations.users import add_user
# Database file path
DB_PATH = "nesha_task_manager.db"

# Custom exception for database operations
class DatabaseError(Exception):
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("task_manager.log"),
        logging.StreamHandler(),
    ],
)

def drop_tables(cursor):
    """Drop all existing tables."""
    logging.warning("Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS TaskResponses;")
    cursor.execute("DROP TABLE IF EXISTS Notifications;")
    cursor.execute("DROP TABLE IF EXISTS RecurringTasks;")
    cursor.execute("DROP TABLE IF EXISTS TaskTags;")
    cursor.execute("DROP TABLE IF EXISTS Tags;")
    cursor.execute("DROP TABLE IF EXISTS AuditLogs;")
    cursor.execute("DROP TABLE IF EXISTS Tasks;")
    cursor.execute("DROP TABLE IF EXISTS Users;")

def create_tables(cursor):
    """Create all necessary tables."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL DEFAULT 'low',
            owner TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            deadline DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner) REFERENCES Users(user_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AuditLogs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            performed_by TEXT NOT NULL,
            FOREIGN KEY (performed_by) REFERENCES Users(user_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TaskResponses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            response_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            comments TEXT,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TaskTags (
            task_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (recipient) REFERENCES Users(user_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RecurringTasks (
            recurring_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_task_id TEXT NOT NULL,
            interval TEXT NOT NULL,
            next_occurrence DATETIME NOT NULL,
            FOREIGN KEY (template_task_id) REFERENCES Tasks(task_id)
        );
    """)

def create_indexes(cursor):
    """Create indexes for performance optimization."""
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON Tasks (status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON Tasks (deadline);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status_deadline ON Tasks (status, deadline);")

def initialize_schema(force: bool = False):
    """Initialize the database schema."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            # Drop tables if force=True
            if force:
                drop_tables(cursor)

            # Create tables and indexes
            create_tables(cursor)
            create_indexes(cursor)

            connection.commit()
            logging.info("Database schema initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize schema: {e}")
        raise DatabaseError("Schema initialization failed.")

def populate_data():
    """Add default users and sample tasks."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            # Add default users
            cursor.execute("""
                INSERT OR IGNORE INTO Users (user_id, name, role)
                VALUES 
                ('user1', 'Manager', 'Manager'),
                ('user2', 'Expert', 'Expert'),
                ('user3', 'Gary', 'User'),
                ('user4', 'Lary', 'User');
            """)

            connection.commit()

        # Add sample tags using `add_tag`
        add_tag('urgent')
        add_tag('review')
        add_tag('bug')
        add_tag('feature')

        logging.info("Sample data added successfully.")
    except Exception as e:
        logging.error(f"Failed to populate data: {e}")
        raise DatabaseError("Data population failed.")

def initialize_db(force: bool = False):
    """Initialize the database schema and populate it with data."""
    initialize_schema(force=force)
    populate_data()

if __name__ == "__main__":
    try:
        initialize_db(force=True)  # Set force=True to reset the database
    except DatabaseError as e:
        logging.error(f"Database initialization failed: {e}")
