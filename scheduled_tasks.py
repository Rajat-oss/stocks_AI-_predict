import time
import threading
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv
import database as db
from telegram_alerts import send_pending_alerts

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scheduled_task(interval_minutes=15):
    """
    Run scheduled tasks at regular intervals
    
    Args:
        interval_minutes: Time between runs in minutes
    """
    while True:
        try:
            logger.info("Running scheduled tasks...")
            
            # Send pending alerts
            alert_count = send_pending_alerts()
            if alert_count > 0:
                logger.info(f"Sent {alert_count} pending alerts")
            
            # Clean up old market data (older than 30 days) to save space
            cleanup_old_data(days=30)
            
            # Wait for the next run
            logger.info(f"Tasks completed. Next run in {interval_minutes} minutes.")
            time.sleep(interval_minutes * 60)
            
        except Exception as e:
            logger.error(f"Error in scheduled tasks: {str(e)}")
            # Wait a bit before retrying
            time.sleep(60)

def cleanup_old_data(days=30):
    """
    Clean up old market data to save database space
    
    Args:
        days: Days to keep (delete data older than this)
    
    Returns:
        Number of records deleted
    """
    try:
        # Use the database function to clean up
        result = db.cleanup_old_data(days=days)
        
        if result > 0:
            logger.info(f"Deleted {result} old market data records")
        
        return result
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        return 0

def start_scheduled_tasks():
    """
    Start the scheduled tasks in a background thread
    """
    thread = threading.Thread(target=run_scheduled_task, daemon=True)
    thread.start()
    logger.info("Scheduled tasks started in background thread")
    return thread

# If run directly, start the scheduled tasks
if __name__ == "__main__":
    thread = start_scheduled_tasks()
    
    try:
        # Keep the main thread alive
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopped by user")