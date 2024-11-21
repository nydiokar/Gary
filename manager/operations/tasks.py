import sqlite3
import logging
from utils import DB_PATH, DatabaseError, TaskStatus, log_action
from operations.notifications import send_notification

def accept_task(task_id: str, user_id: str, comments: str = None) -> None:
    """Accept a task."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT status FROM Tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            if not task:
                raise ValueError(f"Task {task_id} not found.")
            if task[0] != TaskStatus.PENDING.value:
                raise ValueError(f"Task {task_id} is not in Pending state.")

            cursor.execute("""
                UPDATE Tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (TaskStatus.ACCEPTED.value, task_id))
            
            cursor.execute("""
                INSERT INTO TaskResponses (task_id, user_id, action, comments)
                VALUES (?, ?, ?, ?)
            """, (task_id, user_id, TaskStatus.ACCEPTED.value, comments))
            
            connection.commit()

            send_notification(task_id, owner, f"Task {task_id} has been accepted by {user_id}.")
            logging.info(f"Task {task_id} accepted and owner notified.")

        log_action('Tasks', task_id, 'accepted', user_id)
        logging.info(f"Task {task_id} accepted by user {user_id}")

    except Exception as e:
        logging.error(f"Task acceptance failed: {str(e)}")
        raise

def verify_task_with_prompt(task_id: str, user_id: str) -> None:
    """Verify a task with feedback prompt."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT status FROM Tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            if not task or task[0] != TaskStatus.COMPLETED.value:
                raise ValueError(f"Task {task_id} is not in Completed state.")

            while True:
                comments = input("Verification comments (minimum 10 words): ").strip()
                if len(comments.split()) >= 10:
                    break
                print("Feedback must be at least 10 words. Try again.")

            cursor.execute("""
                UPDATE Tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (TaskStatus.VERIFIED.value, task_id))

            cursor.execute("""
                INSERT INTO TaskResponses (task_id, user_id, action, comments)
                VALUES (?, ?, ?, ?)
            """, (task_id, user_id, TaskStatus.VERIFIED.value, comments))

            connection.commit()

        log_action('Tasks', task_id, 'verified', user_id)
        logging.info(f"Task {task_id} verified with feedback")

    except Exception as e:
        logging.error(f"Task verification failed: {str(e)}")
        raise