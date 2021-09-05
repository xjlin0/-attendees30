import pytz, re
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from schedule.models.events import EventRelation


class GatheringBatchCreateResult(object):
    # class Meta:
    #     pass

    def __init__(self, **kwargs):
        for field in ('number_created', 'begin', 'end', 'meet_slug', 'duration'):
            setattr(self, field, kwargs.get(field, None))


class Utility:

    # @property
    # def iso_updated_at(self):
    #     return self.updated.isoformat()

    @property
    def all_notes(self):
        return self.notes.all()

    @staticmethod
    def present_check(string):
        if string:
            return not string.isspace()
        return False

    @staticmethod
    def blank_check(string):
        if string:
            return string.isspace()
        return True

    @staticmethod
    def user_infos():
        return {"settings": {}}

    @staticmethod
    def default_infos():
        return {"fixed": {}, "contacts": {}}

    @staticmethod
    def organization_infos():
        return {
                    "default_time_zone": settings.CLIENT_DEFAULT_TIME_ZONE,
                    "flags": {
                      "attendance_character_to_past_categories":  {}
                    },
                    "groups_see_all_meets_attendees": [],
                    "contacts": {},
                    "counselor": [],
                    "data_admins": [],
                  }

    @staticmethod
    def attendee_infos():
        return {"names": {}, "fixed": {}, "contacts": {}}

    @staticmethod
    def relationship_infos():
        return {"show_secret": {}, "comment": None, "body": None}

    @staticmethod
    def forever():  # 1923 years from now
        return datetime.now(timezone.utc)+timedelta(weeks=99999)

    @staticmethod
    def now_with_timezone(delta=timedelta(weeks=0)):  # 1923 years from now
        return datetime.now(timezone.utc) + delta

    @staticmethod
    def presence(string, default_when_none=None):
        if not string:
            return default_when_none
        else:
            if string.isspace():
                return default_when_none
            else:
                return string.strip()

    @staticmethod
    def parsedate_or_now(date_text, default_format='%Y-%m-%d', default_timezone=pytz.timezone(settings.CLIENT_DEFAULT_TIME_ZONE)):
        parsed_date = Utility.now_with_timezone()
        if isinstance(date_text, str):
            if date_text.count('/') == 2 and default_format.count('-') == 2:
                default_format = '%m/%d/%Y'
            try:
                parsing_datetime = datetime.strptime(date_text, default_format)
                parsed_date = parsing_datetime.astimezone(default_timezone)
            except:
                print("\nCannot parse date for date_text: ", date_text)

        return parsed_date

    @staticmethod
    def boolean_or_datetext_or_original(original_value, strip_first=True):
        boolean_converter = {
            'TRUE': True,
            'FALSE': False,
        }

        if isinstance(original_value, str):
            value = Utility.presence(original_value) if strip_first else original_value
            if value.upper() in boolean_converter:
                return boolean_converter.get(value.upper())
            else:
                try:
                    if value.count('/') == 2:
                        if len(value.split('/')[-1]) > 2:
                            return datetime.strptime(value, '%m/%d/%Y').strftime('%Y-%m-%d')
                        else:
                            return datetime.strptime(value, '%m/%d/%y').strftime('%Y-%m-%d')
                    else:
                        return value
                except ValueError:
                    return value
        else:
            return original_value

    @staticmethod
    def underscore(word):  # https://inflection.readthedocs.io/en/latest/_modules/inflection.html
        word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
        word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
        word = word.replace("-", "_")
        return word.lower()

    @staticmethod
    def get_location(eventrelation):
        model_name, id = eventrelation.distinction.split('#')
        if model_name:
            model = ContentType.objects.filter(model=model_name).first()
            if model:
                target = model.model_class().objects.filter(pk=id).first()
                if object:
                    return str(target)

        return None


    # @property
    # def notes(self):
    #     return Note.objects.filter(
    # #       status=self.status,
    #         link_table=self._meta.db_table,
    #         link_id=self.id
    #     )
