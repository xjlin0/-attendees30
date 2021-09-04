import os, pytz, ssl

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings

from celery.utils.log import get_task_logger

from attendees.occasions.models import Meet, MessageTemplate
from .services.gathering_service import GatheringService

from config import celery_app

logger = get_task_logger(__name__)


@celery_app.task()
def batch_create_gatherings(meet_infos):
    """
    A Celery task to periodically generate gatherings.
    :param meet_infos: a list of meet infos including meet_name, meet_slug, month_adding and recipients' emails
    Todo 20210904 tried regenerate certificates, etc but only one work is to disable it by the following openssl
    """
    try:  # https://stackoverflow.com/a/55320969/4257237
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:  # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:  # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    begin = datetime.utcnow().replace(microsecond=0)
    logger.info(f"batch_create_gatherings task ran at {begin.isoformat()}(UTC) from {__package__}/occasions/tasks.py with {meet_infos}.")
    results = {'email_response': []}
    sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))  # from sendgrid.env

    for meet_info in meet_infos:
        meet = Meet.objects.filter(slug=meet_info['meet_slug']).first()

        if not meet:
            return {'success': False, 'explain': f"Meet with {meet_info['meet_slug']} cannot be found."}

        organization = meet.assembly.division.organization
        mold = MessageTemplate.objects.filter(type='batch_create_gatherings', organization=organization).first()

        if not mold:
            return {'success': False, 'explain': f"MessageTemplate with type 'batch_create_gatherings' under {organization} cannot be found."}

        tzname = meet.infos['default_time_zone'] or organization.infos['default_time_zone'] or settings.CLIENT_DEFAULT_TIME_ZONE
        time_zone = pytz.timezone(tzname)
        end = (datetime.utcnow() + relativedelta(months=+meet_info['months_adding']))
        gathering_results = GatheringService.batch_create(
            begin=begin.isoformat(sep='T', timespec='milliseconds') + 'Z',
            end=end.isoformat(sep='T', timespec='milliseconds') + 'Z',
            meet_slug=meet_info['meet_slug'],
            duration=0,
            meet=meet,
            user_time_zone=time_zone,
        )
        for recipient in meet_info['recipients']:
            mail_variables = {
                    'meet_name': meet_info['meet_name'],
                    'begin': gathering_results['begin'],
                    'end': gathering_results['end'],
                    'tzname': tzname,
                    'env_name': settings.ENV_NAME,
                    'number_created': gathering_results['number_created'],
                    'time_triggered': begin.astimezone(time_zone).strftime('%Y-%m-%d %H:%M%p'),
                    'recipient': recipient,
                }

            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=recipient,
                subject=mold.templates['subject'].format(**mail_variables),
                html_content=mold.templates['html_content'].format(**mail_variables)
                # f"<strong>Dear managers/coworkers:</strong><br>Auto generating gatherings for the meet '{meet_info['meet_name']}' processed,<br>from {gathering_results['begin']} to {gathering_results['end']}({tzname}),<br>{gathering_results['number_created']} gathering(s) created.<br>Best regards,<br>Attendees administrator",
            )  # Todo 20210904 use email template instead
            response = sg.send(message)
            mail_variables['email_status'] = response.status_code
            results['email_log'].append(mold.templates['email_log'].format(**mail_variables))

    return results

# in /admin/django_celery_beat/periodictask/  select the registered task and add Keyword Arguments: {"meet_slugs": ["a","b","c"] }
# celeryworker    | [2021-08-27 15:12:43,629: INFO/MainProcess] Received task: attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]
# celeryworker    | [2021-08-27 15:12:43,630: INFO/ForkPoolWorker-1] attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5]: The sample task just ran from {app_name}/occasions/tasks.py.
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] test desc: attendees.occasions.tasks.batch_create_gatherings
# celeryworker    | [2021-08-27 15:12:43,631: WARNING/ForkPoolWorker-1] ['a', 'b', 'c']
# celeryworker    | [2021-08-27 15:12:43,645: INFO/ForkPoolWorker-1] Task attendees.occasions.tasks.batch_create_gatherings[2c862cdd-debf-4c65-817b-aa54dda805f5] succeeded in 0.014808513999923889s: 42
