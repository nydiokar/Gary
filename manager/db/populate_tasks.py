import sqlite3
from datetime import datetime, timedelta

DB_PATH = "nesha_task_manager.db"

def populate_tasks():
    """Populate the database with sample tasks."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            # Sample users
            cursor.execute("""
                INSERT OR IGNORE INTO Users (user_id, name, role)
                VALUES 
                ('user1', 'Alex', 'Manager'),
                ('user2', 'Sarah', 'Expert'),
                ('user3', 'John', 'User')
            """)

            # Sample tasks
            cursor.execute("""
                INSERT OR IGNORE INTO Tasks (title, description, priority, owner, status, deadline, created_at)
                VALUES 
                ('Prepare report', 'Monthly financial report', 'low', 'user1', 'Pending', ?, ?),
                ('Code review', 'Review PR #42', 'medium', 'user2', 'In Progress', ?, ?),
                ('Update website', 'Update homepage banner', 'high', 'user3', 'Pending', ?, ?)
            """, (
                (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                (datetime.now() + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

            connection.commit()
            print("Sample tasks and users populated successfully.")
    except Exception as e:
        print(f"Error populating database: {e}")

if __name__ == "__main__":
    populate_tasks()
