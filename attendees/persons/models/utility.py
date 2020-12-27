import pytz
from datetime import datetime, timedelta, timezone
from django.conf import settings


class Utility:

    # @property
    # def iso_updated_at(self):
    #     return self.updated.isoformat()

    @property
    def all_notes(self):
        return self.notes.all()

    @staticmethod
    def default_infos():
        return {"flexible": {}, "fixed": {}}

    @staticmethod
    def forever():  # 1923 years from now
        return datetime.now(timezone.utc)+timedelta(weeks=99999)

    @staticmethod
    def now_with_timezone():  # 1923 years from now
        return datetime.now(timezone.utc)

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

    # @property
    # def notes(self):
    #     return Note.objects.filter(
    # #       status=self.status,
    #         link_table=self._meta.db_table,
    #         link_id=self.id
    #     )
