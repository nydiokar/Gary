import re
from datetime import datetime
from manager.task_management import from_command, TaskManager  # TaskManager from task_management.py
import logging
task_manager = TaskManager()

def process_command(command: str) -> str:
    try:
        # Add Task
        if command.startswith("/add_task"):
            match = re.match(r"/add_task '(.+)' '(.+)' (\w+) (\w+) '(.+)'", command)
            if match:
                title, description, priority, owner, deadline = match.groups()
                task_id = task_manager.create_task(title, description, priority.lower(), owner, deadline)
                return f"Task '{title}' created with ID: {task_id}"
            else:
                return "Error: Invalid syntax for /add_task. Use: /add_task 'title' 'description' priority owner 'deadline'"

        # Update Task Status
        elif command.startswith("/update_task"):
            match = re.match(r"/update_task (\w+) (\w+)", command)
            if match:
                task_id, status = match.groups()
                result = task_manager.update_task_status(task_id, status)
                return result or f"Task {task_id} updated to status: {status}"
            else:
                return "Error: Invalid syntax for /update_task. Use: /update_task task_id status"

        # Delegate Task
        elif command.startswith("/delegate_task"):
            match = re.match(r"/delegate_task (\w+) (\w+)", command)
            if match:
                task_id, owner = match.groups()
                result = task_manager.delegate_task(task_id, owner)
                return result or f"Task {task_id} delegated to {owner}."
            else:
                return "Error: Invalid syntax for /delegate_task. Use: /delegate_task task_id owner"

        # Delete Task
        elif command.startswith("/delete_task"):
            match = re.match(r"/delete_task (\w+)", command)
            if match:
                task_id = match.groups()[0]
                result = task_manager.delete_task(task_id)
                return result or f"Task {task_id} deleted."
            else:
                return "Error: Invalid syntax for /delete_task. Use: /delete_task task_id"

        # List Tasks
        elif command.startswith("/list_tasks"):
            tasks = task_manager.list_tasks()
            if tasks:
                return "\n".join(tasks)
            return "No tasks found."

        # List Overdue Tasks
        elif command.startswith("/overdue_tasks"):
            overdue_tasks = task_manager.list_overdue_tasks()
            if overdue_tasks:
                return "\n".join([f"task_{task['task_id']}: {task['title']} (Owner: {task['owner']}) - Overdue!" for task in overdue_tasks])
            return "No overdue tasks."

        # Task Details
        elif command.startswith("/task_details"):
            match = re.match(r"/task_details (\d+)", command)
            if match:
                task_id = int(match.groups()[0])
                task = task_manager.get_task_details(task_id)
                if task:
                    return (f"Task ID: task_{task['task_id']}\n"
                    f"Title: {task['title']}\n"
                    f"Description: {task['description']}\n"
                    f"Priority: {task['priority']} Priority\n"
                    f"Owner: {task['owner']}\n"
                    f"Status: {task['status']}\n"
                    f"Deadline: {task['deadline']}\n"
                    f"Created At: {task['created_at']}\n"
                    f"Updated At: {task['updated_at']}")
                return f"Task {task_id} not found."
            else:
                return "Error: Invalid syntax for /task_details. Use: /task_details task_id"

        # Notifications Placeholder
        elif command.startswith("/notifications"):
             return "Feature not implemented yet. # Implement listing notifications"

        # Recurring Tasks Placeholder
        elif command.startswith("/recurring_tasks"):
            return "Feature not implemented yet. # Implement recurring tasks list"

        # Unknown Command
        else:
            return "Unknown command. Please use a valid command."

    except Exception as e:
        logging.error(f"Error processing command: {e}")
        return f"Error processing command: {e}"