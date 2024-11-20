import logging
from manager.utils import DB_PATH, SYSTEM_USER_ID, UserRole, log_action, DatabaseError
from ..operations.users import add_user
from ..operations.tags import add_tag
from .db_initialize import check_existing_tables

def initialize_system_data() -> None:
    """Initialize essential system data."""
    try:
        add_user(SYSTEM_USER_ID, "System", UserRole.SYSTEM.value)
        log_action('Database', 'system', 'system_initialization', SYSTEM_USER_ID)
        logging.info("System data initialized successfully.")
    except Exception as e:
        logging.error(f"System data initialization failed: {str(e)}")
        raise

def add_sample_data() -> None:
    """Add sample data for development/testing."""
    try:
        # Check if tables exist
        tables = check_existing_tables()
        if not tables:
            raise DatabaseError("No tables found. Initialize schema first.")
        
        # Add sample users
        add_user('user1', 'Nesha', UserRole.MANAGER.value)
        add_user('user2', 'Duman', UserRole.EXPERT.value)
        add_user('user3', 'Gary', UserRole.USER.value)
        add_user('user4', 'Lary', UserRole.USER.value)

        # Add sample tags
        add_tag('urgent')
        add_tag('review')
        add_tag('bug')
        add_tag('feature')

        logging.info("Sample data added successfully.")
    except DatabaseError as e:
        logging.error(f"Sample data addition failed: {str(e)}")
        raise
    

