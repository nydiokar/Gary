# operations/recurring_tasks.py
import sqlite3
import logging
from manager.utils import log_action, DB_PATH
from datetime import datetime, timedelta
def schedule_recurring_task(template_task_id: str, interval: str, next_occurrence: str) -> None:
    """Add a recurring task."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO RecurringTasks (template_task_id, interval, next_occurrence)
                VALUES (?, ?, ?)
            """, (template_task_id, interval, next_occurrence))
            recurring_task_id = cursor.lastrowid
            connection.commit()

        log_action('RecurringTasks', str(recurring_task_id), 'recurring_task_added', 'system')
        logging.info(f"Recurring task {recurring_task_id} scheduled successfully.")
    except Exception as e:
        logging.error(f"Failed to schedule recurring task: {e}")
        raise

def process_recurring_tasks():
    """Process recurring tasks and create new tasks if their next occurrence is due."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()

            # Fetch all recurring tasks where next_occurrence is due
            cursor.execute("""
                SELECT recurring_task_id, template_task_id, interval, next_occurrence
                FROM RecurringTasks
                WHERE next_occurrence <= datetime('now')
            """)
            recurring_tasks = cursor.fetchall()

            for task in recurring_tasks:
                recurring_task_id, template_task_id, interval, next_occurrence = task

                # Fetch template task details
                cursor.execute("SELECT * FROM Tasks WHERE task_id = ?", (template_task_id,))
                template_task = cursor.fetchone()
                if not template_task:
                    logging.warning(f"Template task {template_task_id} not found. Skipping.")
                    continue

                # Create a new task based on the template
                new_task_id = f"{template_task_id}_{next_occurrence.replace(' ', '_')}"
                cursor.execute("""
                    INSERT INTO Tasks (task_id, title, description, priority, owner, status, deadline, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'Pending', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (new_task_id, *template_task[1:5]))

                # Calculate and update the next_occurrence
                next_occurrence_dt = datetime.strptime(next_occurrence, '%Y-%m-%d %H:%M:%S')
                if interval == 'daily':
                    next_occurrence_dt += timedelta(days=1)
                elif interval == 'weekly':
                    next_occurrence_dt += timedelta(weeks=1)
                elif interval == 'monthly':
                    next_occurrence_dt += timedelta(days=30)  # Approximation

                cursor.execute("""
                    UPDATE RecurringTasks
                    SET next_occurrence = ?
                    WHERE recurring_task_id = ?
                """, (next_occurrence_dt.strftime('%Y-%m-%d %H:%M:%S'), recurring_task_id))

            connection.commit()
        logging.info("Processed all due recurring tasks.")
    except Exception as e:
        logging.error(f"Failed to process recurring tasks: {e}")
        raise

