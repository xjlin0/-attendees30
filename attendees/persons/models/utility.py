from datetime import datetime, timedelta, timezone


class Utility:

    # @property
    # def iso_updated_at(self):
    #     return self.updated.isoformat()

    @property
    def all_notes(self):
        return self.notes.all()

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

    # @property
    # def notes(self):
    #     return Note.objects.filter(
    # #       status=self.status,
    #         link_table=self._meta.db_table,
    #         link_id=self.id
    #     )
