import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings

from celery.utils.log import get_task_logger

from attendees.occasions.models import Meet
from .services.gathering_service import GatheringService

from config import celery_app

logger = get_task_logger(__name__)

@celery_app.task()
def batch_create_gatherings(meet_infos):
    """
    A Celery task to periodically generate gatherings.
    :param meet_slugs: a dictionary of meet_slug: [email_recipients]
    """
    logger.info("The sample task just ran from {app_name}/occasions/tasks.py.")
    print("test desc: attendees.occasions.tasks.batch_create_gatherings")
    print(meet_infos)
    results = {}

    for meet_slug, recipients in meet_infos.items():
        meet = Meet.objects.filter(slug=meet_slug).first()
        if meet:
            organization = meet.assembly.division.organization
            tzname = meet.infos['default_time_zone'] or organization.infos['default_time_zone'] or settings.CLIENT_DEFAULT_TIME_ZONE
            time_zone = pytz.timezone(tzname)
            results = GatheringService.batch_create(
                begin=datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + 'Z',
                end=(datetime.utcnow() + relativedelta(months=+1)).isoformat(sep='T', timespec='milliseconds') + 'Z',
                meet_slug=meet_slug,
                meet=meet,
                user_time_zone=time_zone,
            )
            print("hi 37 here is results: "); print(results)
    return results

# in /admin/django_celery_beat/periodictask/  select the registered task and add Keyword Arguments: {"meet_slugs": ["a","b","c"] }
# celeryworker    | [2021-08-27 15:12:43,629: INFO/MainProcess] Received task: attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]
# celeryworker    | [2021-08-27 15:12:43,630: INFO/ForkPoolWorker-1] attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]: The sample task just ran from {app_name}/occasions/tasks.py.
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] test desc: attendees.occasions.tasks.batch_create_gatherings
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] ['a', 'b', 'c']
# celeryworker    | [2021-08-27 15:12:43,645: INFO/ForkPoolWorker-1] Task attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5] succeeded in 0.014808513999923889s: 42
