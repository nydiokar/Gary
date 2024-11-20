import datetime
from typing import Dict, List
import sqlite3
import datetime
from manager.utils import DB_PATH, log_action
from operations.notifications import send_notification
import re
from datetime import timedelta

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
            task_id=f"task_{int(datetime.datetime.now().timestamp())}",
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
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)

    def create_task(self, name: str, priority: int, owner: str, deadline=None) -> str:
        """Create a new task and add it to the database."""
        task_id = f"task_{int(datetime.datetime.now().timestamp())}"  # Unique ID based on timestamp
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Tasks (task_id, title, priority, owner, status, deadline, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'Pending', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (task_id, name, priority, owner, deadline))
                log_action('Tasks', task_id, 'creation', owner)
            print(f"Task Created: {name} (ID: {task_id})")
        except Exception as e:
            print(f"Error creating task: {e}")
            raise
        return task_id

    def delegate_task(self, task_id: str, agent_name: str):
        """Update the status of a task to 'In Progress' and log the action."""
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Tasks SET status = 'In Progress', updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ? AND status = 'Pending'
                """, (task_id,))
                if cursor.rowcount == 0:
                    print(f"Task {task_id} not found or not in Pending status.")
                    return
                log_action('Tasks', task_id, 'delegated', agent_name)
            print(f"Task {task_id} delegated to {agent_name}.")
        except Exception as e:
            print(f"Error delegating task: {e}")
            raise

    def update_task_status(self, task_id: str, status: str):
        """Update the status of a task."""
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Tasks SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """, (status, task_id))
                if cursor.rowcount == 0:
                    print(f"Task {task_id} not found.")
                    return
                log_action('Tasks', task_id, 'status_update', 'system')
            print(f"Task {task_id} updated to status: {status}.")
        except Exception as e:
            print(f"Error updating task status: {e}")
            raise

    def audit_tasks(self):
        """Audit tasks to check for overdue ones and notify owners."""
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT task_id, owner, deadline FROM Tasks
                    WHERE status != 'Completed' AND deadline <= datetime('now')
                """)
                overdue_tasks = cursor.fetchall()
                for task_id, owner, deadline in overdue_tasks:
                    message = f"Task {task_id} is overdue! Please take action."
                    send_notification(task_id, owner, message)
                    print(f"Notification sent to {owner}: {message}")
        except Exception as e:
            print(f"Error auditing tasks: {e}")
            raise

    def get_task(self, task_id: str):
        """Fetch a task from the database."""
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,))
                task = cursor.fetchone()
                if not task:
                    print(f"Task {task_id} not found.")
                    return None
                return task
        except Exception as e:
            print(f"Error fetching task: {e}")
            raise
