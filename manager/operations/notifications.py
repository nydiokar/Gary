# operations/notifications.py
import sqlite3
import logging
from manager.utils import log_action, DB_PATH

def send_notification(task_id: str, recipient: str, message: str) -> None:
    """Log a notification in the database."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Notifications (task_id, recipient, message)
                VALUES (?, ?, ?)
            """, (task_id, recipient, message))
            connection.commit()

        log_action('Notifications', task_id or 'general', 'notification_sent', 'system')
        logging.info(f"Notification sent to {recipient}: {message}")
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")
        raise

def fetch_notifications(recipient: str) -> list:
    """Fetch notifications for a specific recipient."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM Notifications WHERE recipient = ? ORDER BY timestamp DESC
            """, (recipient,))
            notifications = cursor.fetchall()
        return notifications
    except Exception as e:
        logging.error(f"Failed to fetch notifications for {recipient}: {e}")
        raise
