import sqlite3
from manager.utils import DB_PATH, log_action
from manager.operations.notifications import send_notification
import re
from datetime import datetime, timedelta
from collections import namedtuple

def from_command(command: str) -> dict:
    """Extract task details from a natural language command."""
    # Example parsing logic using regex
    title_match = re.search(r"task to (.*?)(,| with)", command)
    deadline_match = re.search(r"deadline (.*?)(\.|$)", command)
    priority_match = re.search(r"priority (\d+)", command)
    owner_match = re.search(r"assign it to (\w+)", command)

    # Extracted data
    title = title_match.group(1).strip() if title_match else "Untitled Task"
    deadline_str = deadline_match.group(1).strip() if deadline_match else None
    priority = int(priority_match.group(1)) if priority_match else 1
    owner = owner_match.group(1).strip() if owner_match else "default_user"

    # Convert deadline to datetime if applicable
    deadline = None
    if deadline_str:
        if "tomorrow" in deadline_str:
            deadline = datetime.now() + timedelta(days=1)
        elif "today" in deadline_str:
            deadline = datetime.now()
        else:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("Invalid deadline format. Use 'YYYY-MM-DD HH:MM:SS'.")

    return {
        "name": title,
        "priority": priority,
        "owner": owner,
        "deadline": deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None,
    }

# Task Class
class Task:
    def __init__(self, task_id, name, priority, owner, status="Pending", deadline=None, created_at=None, updated_at=None):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.owner = owner
        self.status = status
        self.deadline = deadline
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or self.created_at

    @classmethod
    def from_db_row(cls, row):
        """Create a Task object from a database row."""
        return cls(*row)

    @classmethod
    def from_command(cls, command: dict):
        """Create a Task object from parsed command details."""
        return cls(
            task_id = f"task_{int(datetime.now().timestamp())}",
            name=command["name"],
            priority=command.get("priority", 1),
            owner=command.get("owner", "user1"),
            deadline=command.get("deadline"),
        )

    def is_overdue(self):
        """Check if the task is overdue."""
        if self.deadline:
            deadline_dt = datetime.datetime.strptime(self.deadline, '%Y-%m-%d %H:%M:%S')
            return datetime.datetime.now() > deadline_dt
        return False

    def save_to_db(self):
        """Save or update the task in the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Tasks (task_id, title, priority, owner, status, deadline, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    title = excluded.title,
                    priority = excluded.priority,
                    owner = excluded.owner,
                    status = excluded.status,
                    deadline = excluded.deadline,
                    updated_at = excluded.updated_at
            """, (self.task_id, self.name, self.priority, self.owner, self.status, self.deadline, self.created_at, self.updated_at))
            conn.commit()
        log_action('Tasks', self.task_id, 'save', self.owner)

    def to_dict(self):
        """Convert the Task object to a dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "priority": self.priority,
            "owner": self.owner,
            "status": self.status,
            "deadline": self.deadline,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


# TaskManager Class
class TaskManager:
    def create_task(self, title, description, priority, owner, deadline):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Tasks (title, description, priority, owner, deadline)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, priority, owner, deadline))
            connection.commit()
            return cursor.lastrowid

    def update_task_status(self, task_id, status):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task_id FROM Tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            if not task:
                return f"Task {task_id} not found."
        
            cursor.execute("""
                UPDATE Tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (status, task_id))
            connection.commit()
            return f"Task {task_id} updated to status: {status}"

    def delegate_task(self, task_id, new_owner):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task_id FROM Tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            if not task:
                return f"Task {task_id} not found."
        
            cursor.execute("""
                UPDATE Tasks
                SET owner = ?, status = 'In Progress', updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (new_owner, task_id))
            connection.commit()
            return f"Task {task_id} delegated to {new_owner}."

    def delete_task(self, task_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task_id FROM Tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            if not task:
                return f"Task {task_id} not found."
        
            cursor.execute("""
                DELETE FROM Tasks
                WHERE task_id = ?
            """, (task_id,))
            connection.commit()
            return f"Task {task_id} deleted successfully."

    def list_tasks(self):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT task_id, title, priority, owner, status
                FROM Tasks
            """)
            tasks = cursor.fetchall()
            if tasks:
                return [
                    f"task_{task[0]}: {task[1]} ({task[2].capitalize()} Priority, Owner: {task[3]}) - {task[4]}"
                    for task in tasks
                ]
            return []

    def list_overdue_tasks(self):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT task_id, title, owner, status, deadline
                FROM Tasks
                WHERE deadline < CURRENT_TIMESTAMP AND status != 'Completed'
            """)
            overdue_tasks = cursor.fetchall()
            if overdue_tasks:
                return [
                    {"task_id": task[0], "title": task[1], "owner": task[2], "status": task[3], "deadline": task[4]}
                    for task in overdue_tasks
                ]
            return []

    def get_task(self, task_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                Task = namedtuple("Task", [desc[0] for desc in cursor.description])
                return Task(*row)
            return None

    def get_task_details(self, task_id):
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT task_id, title, description, priority, owner, status, deadline, created_at, updated_at
                FROM Tasks
                WHERE task_id = ?
            """, (task_id,))
            task = cursor.fetchone()
            if task:
                return {
                    "task_id": task[0],
                    "title": task[1],
                    "description": task[2] or "No description provided",
                    "priority": task[3].capitalize(),
                    "owner": task[4],
                    "status": task[5],
                    "deadline": task[6],
                    "created_at": task[7],
                    "updated_at": task[8]
                }
            return None