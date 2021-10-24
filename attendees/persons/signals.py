from django.db.models.signals import post_save
from django.dispatch import receiver

from attendees.occasions.models import Meet
from attendees.persons.models import Utility, AttendingMeet
from .models import Past


@receiver(post_save, sender=Past)
def post_save_handler_for_past_to_create_attendingmeet(sender, **kwargs):
    """
    To let user easily spot certain attendee attributes, here is automatic creation
    of AttendingMeet after creating Past of certain categories in Organization.infos

    :param sender: sender Class
    :param kwargs:
    :return: None
    """
    if not kwargs.get('raw') and kwargs.get('created'):  # to skip extra creation in loaddata seed
        created_past = kwargs.get('instance')
        organization = created_past.organization
        category_id = str(created_past.category.id)  # json can only have string as key, not numbers
        meet_id = organization.infos.get('settings', {}).get('past_category_to_attendingmeet_meet', {}).get(category_id)
        if meet_id:
            meet = Meet.objects.filter(pk=meet_id).first()
            if meet:
                target_attendee = created_past.subject
                first_attending = target_attendee.attendings.first()
                if first_attending:
                    defaults = {'character': meet.major_character, 'finish': Utility.forever()}
                    if created_past.when:
                        defaults['start'] = created_past.when
                    Utility.update_or_create_last(
                        AttendingMeet,
                        update=False,
                        filters={'meet': meet, 'attending': first_attending, 'is_removed': False},
                        defaults=defaults,
                    )


