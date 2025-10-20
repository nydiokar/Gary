# Gary - Task Management System

## Overview

Gary is a comprehensive task management application designed for teams and individuals to efficiently manage tasks, deadlines, and workflows. Built with Python and SQLite, it provides a robust foundation for task tracking with advanced features like recurring tasks, notifications, user management, and audit logging.

## What This Project Is About

Gary is a command-line task management system that allows users to:

- **Create and manage tasks** with priorities, deadlines, and ownership
- **Track task progress** through different status stages
- **Handle recurring tasks** that automatically generate new instances
- **Send notifications** for task updates and deadlines
- **Tag tasks** for better organization and filtering
- **Maintain audit logs** for all task-related activities
- **Support multiple users** with different roles and permissions

The system is designed to be extensible and can serve as a foundation for more complex project management tools.

## Key Features

### ✅ Currently Implemented

#### Core Task Management
- **Task Creation**: Create tasks with title, description, priority, owner, and deadline
- **Task Updates**: Modify task status, ownership, and other properties
- **Task Delegation**: Transfer task ownership between users
- **Task Deletion**: Remove tasks from the system
- **Task Listing**: View all tasks with filtering options
- **Overdue Task Tracking**: Identify and list overdue tasks

#### Advanced Features
- **Recurring Tasks**: Automatically generate new tasks based on schedules (daily, weekly, monthly)
- **User Management**: Support for multiple users with roles (Manager, Expert, User)
- **Tagging System**: Categorize tasks with custom tags
- **Audit Logging**: Track all changes and actions performed on tasks
- **Notification System**: Basic notification framework (logging-based)

#### Data Management
- **SQLite Database**: Persistent storage with proper schema design
- **Database Initialization**: Automated setup and sample data population
- **Background Processing**: Automated recurring task processing via scheduler

### 🚧 Partially Implemented

#### Notifications
- Database structure exists for notifications
- Basic logging functionality implemented
- **Missing**: Email/SMS integration, real-time notifications, notification preferences

#### Command Interface
- Basic command parsing and processing exists
- **Missing**: Full CLI interface, interactive mode, command history

### 🔮 Future Potential

#### Enhanced User Experience
- **Web Interface**: REST API + web frontend for better usability
- **Mobile App**: React Native or Flutter app for mobile access
- **Desktop GUI**: Electron-based desktop application

#### Advanced Features
- **Task Dependencies**: Link tasks that depend on each other
- **Time Tracking**: Log time spent on tasks
- **File Attachments**: Attach documents and files to tasks
- **Comments/Discussions**: Add comments to tasks for collaboration
- **Task Templates**: Save and reuse common task patterns
- **Reporting/Dashboard**: Analytics and progress reporting
- **Integration APIs**: Connect with external tools (Slack, Jira, etc.)

#### Scalability Improvements
- **Multi-database Support**: PostgreSQL, MySQL for larger deployments
- **Caching Layer**: Redis for improved performance
- **Microservices Architecture**: Break into smaller, focused services
- **Cloud Deployment**: Docker containers, Kubernetes orchestration

## Architecture

```
gary/
├── manager/
│   ├── main.py              # Application entry point and scheduler
│   ├── commands.py          # Command parsing and processing
│   ├── task_management.py   # Core task management logic
│   ├── utils.py             # Utility functions and database connection
│   ├── db/
│   │   ├── db_initialize.py # Database schema and initialization
│   │   ├── populate.py      # Sample data population
│   │   └── populate_tasks.py
│   └── operations/
│       ├── notifications.py # Notification system
│       ├── recurring_tasks.py # Recurring task processing
│       ├── tags.py          # Tag management
│       └── users.py         # User management
```

## Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE Users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tasks
```sql
CREATE TABLE Tasks (
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
```

#### RecurringTasks
```sql
CREATE TABLE RecurringTasks (
    recurring_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_task_id TEXT NOT NULL,
    interval TEXT NOT NULL,
    next_occurrence DATETIME NOT NULL,
    FOREIGN KEY (template_task_id) REFERENCES Tasks(task_id)
);
```

#### Notifications
```sql
CREATE TABLE Notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    recipient TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (recipient) REFERENCES Users(user_id)
);
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- SQLite3 (usually included with Python)
- APScheduler for recurring tasks

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gary
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install apscheduler
   ```

4. **Initialize the database**
   ```python
   cd manager
   python db/db_initialize.py
   ```

5. **Run the application**
   ```python
   python main.py
   ```

### Configuration

The application uses the following default configuration:
- Database: `nesha_task_manager.db`
- Log file: `task_manager.log`
- Default users: Manager, Expert, Gary, Lary

## Usage

### Command-Line Interface

The system supports various commands for task management:

```bash
# Add a new task
python -c "from manager.commands import process_command; print(process_command(\"/add_task 'Complete project' 'Finish the documentation' 'high' 'user1' '2024-12-31 23:59:59'\"))"

# Update task status
python -c "from manager.commands import process_command; print(process_command(\"/update_task 1 'In Progress'\"))"

# List all tasks
python -c "from manager.commands import process_command; print(process_command(\"/list_tasks\"))"

# Get overdue tasks
python -c "from manager.commands import process_command; print(process_command(\"/overdue_tasks\"))"
```

### Programmatic Usage

```python
from manager.task_management import TaskManager

# Initialize task manager
task_manager = TaskManager()

# Create a task
task_id = task_manager.create_task(
    title="Review documentation",
    description="Review and approve project documentation",
    priority="high",
    owner="user1",
    deadline="2024-12-31 23:59:59"
)

# Update task status
result = task_manager.update_task_status(task_id, "Completed")

# List all tasks
tasks = task_manager.list_tasks()
```

## Development Status

### What's Working
- ✅ Database schema and initialization
- ✅ Basic CRUD operations for tasks
- ✅ Recurring task processing
- ✅ User management and authentication framework
- ✅ Audit logging system
- ✅ Tag system foundation

### What Needs Work
- 🔄 Notification delivery system (currently only logs to database)
- 🔄 Command-line interface improvements
- 🔄 Input validation and error handling
- 🔄 Testing framework
- 🔄 Configuration management

### Critical Path to Minimum Viable Product (MVP)

1. **Complete Notification System**
   - Implement email notifications
   - Add notification preferences
   - Create notification templates

2. **Improve User Interface**
   - Create interactive CLI mode
   - Add command history and auto-completion
   - Implement better error messages

3. **Add Data Validation**
   - Input sanitization
   - Business rule validation
   - Error recovery mechanisms

4. **Testing and Documentation**
   - Unit tests for core functionality
   - Integration tests for database operations
   - User documentation and API reference

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Write docstrings for all public functions
- Add comments for complex business logic

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation for common solutions

---

**Note**: This project appears to be in active development. Some features may be incomplete or subject to change. The recurring tasks and notification systems show particular promise for automation workflows.
