from celery.utils.log import get_task_logger
from celery import shared_task
from services.services import CurrencyServices

logger = get_task_logger(__name__)

@shared_task
def debug_task():
     logger.info("Task executed.")

@shared_task
def get_rate():
    CurrencyServices.get_rate()


