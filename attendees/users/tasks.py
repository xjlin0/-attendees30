from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from config import celery_app

User = get_user_model()
logger = get_task_logger(__name__)

@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    logger.info("The sample task just ran from {app_name}/users/tasks.py.")
    print("hi in get_users_count")
    return User.objects.count()
