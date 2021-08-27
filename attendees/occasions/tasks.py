import pytz
from django.conf import settings
from urllib import parse

from celery.utils.log import get_task_logger

from attendees.occasions.models import Meet
from .services.gathering_service import GatheringService

from config import celery_app

logger = get_task_logger(__name__)

@celery_app.task()
def batch_create_gatherings(meet_slugs):
    """A Celery task to periodically generate gatherings."""
    logger.info("The sample task just ran from {app_name}/occasions/tasks.py.")
    print("test desc: attendees.occasions.tasks.batch_create_gatherings")
    print(meet_slugs)
    # tzname = settings.CLIENT_DEFAULT_TIME_ZONE
    #
    # for meet_slug in meet_slugs:
    #     meet = Meet.objects.filter(slug=meet_slug).first()
    #     if meet:
    #         results = GatheringService.batch_create(
    #             begin='',
    #             end='',
    #             meet_slug=meet_slug,
    #             user_organization=meet.assembly.division.organization,
    #             user_time_zone=pytz.timezone(parse.unquote(tzname)),
    #         )

    return 42

# in /admin/django_celery_beat/periodictask/  select the registered task and add Keyword Arguments: {"meet_slugs": ["a","b","c"] }
# celeryworker    | [2021-08-27 15:12:43,629: INFO/MainProcess] Received task: attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]
# celeryworker    | [2021-08-27 15:12:43,630: INFO/ForkPoolWorker-1] attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]: The sample task just ran from {app_name}/occasions/tasks.py.
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] test desc: attendees.occasions.tasks.batch_create_gatherings
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] ['a', 'b', 'c']
# celeryworker    | [2021-08-27 15:12:43,645: INFO/ForkPoolWorker-1] Task attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5] succeeded in 0.014808513999923889s: 42
