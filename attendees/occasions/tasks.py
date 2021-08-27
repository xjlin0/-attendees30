from celery.utils.log import get_task_logger
from .services.gathering_service import GatheringService

from config import celery_app

logger = get_task_logger(__name__)

@celery_app.task()
def batch_create_gatherings():
    """A pointless Celery task to demonstrate usage."""
    logger.info("The sample task just ran from {app_name}/occasions/tasks.py.")
    print("hi in batch_create_gatherings")
    return 42


# celeryworker    | [2021-08-20 00:31:09,625: INFO/MainProcess] Received task: attendees.users.tasks.get_users_count[0bab35ca-ff52-4e01-8e46-d30f6554c3d0]
# celeryworker    | [2021-08-20 00:31:09,626: INFO/ForkPoolWorker-1] attendees.users.tasks.get_users_count[0bab35ca-ff52-4e01-8e46-d30f6554c3d0]: The sample task just ran from {app_name}/users/tasks.py.
# celeryworker    | [2021-08-20 00:31:09,626: WARNING/ForkPoolWorker-1] hi 13
# celeryworker    | [2021-08-20 00:31:09,644: INFO/ForkPoolWorker-1] Task attendees.users.tasks.get_users_count[0bab35ca-ff52-4e01-8e46-d30f6554c3d0] succeeded in 0.018400422006379813s: 2
