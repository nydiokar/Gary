import logging
from db.db_initialize import initialize_db
from utils import DatabaseError
from apscheduler.schedulers.background import BackgroundScheduler
from operations.recurring_tasks import process_recurring_tasks

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('task_manager.log'),
            logging.StreamHandler()
        ]
    )

def initialize_scheduler():
    """Initialize the scheduler for recurring tasks."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_recurring_tasks, 'interval', hours=1)  # Runs every hour
    scheduler.start()
    logging.info("Scheduler initialized.")

def initialize_application(dev_mode: bool = False) -> None:
    """Initialize the entire application."""
    try:
        setup_logging()
        initialize_db(force=dev_mode)  # Initialize schema and populate data
        
        initialize_scheduler()  # Initialize the recurring task scheduler
        
        logging.info("Application initialized successfully.")
    except DatabaseError as e:
        logging.error(f"Failed to initialize application: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during application initialization: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        initialize_application(dev_mode=True)  # Set to False for production
    except Exception as e:
        logging.error(f"Application startup failed: {str(e)}")
