from django.db.models import Q
from attendees.occasions.models import Gathering, Meet
from datetime import datetime, timedelta

class GatheringService:

    @staticmethod
    def by_assembly_meets(assembly_slug, meet_slugs):
        return Gathering.objects.filter(
                    meet__slug__in=meet_slugs,
                    meet__assembly__slug=assembly_slug,
                ).order_by(
                    'meet',
                    '-start',
                )

    @staticmethod
    def by_family_meets(user, meet_slugs):
        """
        :query: Find all gatherings of all Attendances of the current user and their kid/care receiver, so all
                their "family" attending gatherings (including not joined characters) will show up.
        :param user: user object
        :param meet_slugs:
        :return:  all Gatherings of the logged in user and their kids/care receivers.
        """
        return Gathering.objects.filter(
            Q(meet__in=user.attendee.attendings.values_list('gathering__meet'))
            |
            Q(meet__in=user.attendee.related_ones.filter(
                from_attendee__scheduler=True
            ).values_list('attendings__gathering__meet')),
            meet__slug__in=meet_slugs,
            meet__assembly__division__organization__slug=user.organization.slug,
        ).order_by(
            'meet',
            '-start',
        )  # another way is to get assemblys from registration, but it relies on attendingmeet validations

    @staticmethod
    def by_organization_meets(current_user, meet_slugs, start, finish):
        filters = Q(meet__assembly__division__organization__slug=current_user.organization.slug).add(
                        Q(meet__slug__in=meet_slugs), Q.AND)

        if not current_user.can_see_all_organizational_meets_attendees():
            filters.add(Q(attendings__attendee=current_user.attendee), Q.AND)

        if start:
            filters.add((Q(finish__isnull=True) | Q(finish__gte=start)), Q.AND)
        if finish:
            filters.add((Q(start__isnull=True) | Q(start__lte=finish)), Q.AND)
        return Gathering.objects.filter(filters).order_by(
            'meet',
            '-start',
        )

    @staticmethod
    def batch_create(begin, end, meet_slug, duration, user_organization, user_time_zone):
        """
        Ideopotently create gatherings based on the following params.  Created Gatherings are associated with Occurrence
        Todo 20210821 Hardcoded tzinfo for strptime to get event.get_occurrences() working as of now, needs improvement.
        :param begin:
        :param end:
        :param meet_slug:
        :param duration:
        :param user_organization:
        :param user_time_zone:
        :return: number of gatherings created
        """
        number_created = 0
        iso_time_format = '%Y-%m-%dT%H:%M:%S.%f%z'
        begin_time = datetime.strptime(begin, iso_time_format).astimezone(user_time_zone)
        end_time = datetime.strptime(end, iso_time_format).astimezone(user_time_zone)
        meet = Meet.objects.filter(slug=meet_slug, assembly__division__organization=user_organization).first()

        if meet and end_time > begin_time:
            gathering_time = timedelta(minutes=duration) if duration and duration > 0 else None
            for er in meet.event_relations.all():
                for occurrence in er.event.get_occurrences(begin_time, end_time):
                    occurrence_end = occurrence.start + gathering_time if gathering_time else occurrence.end
                    gathering, gathering_created = Gathering.objects.get_or_create(
                        meet=meet,
                        site_id=meet.site_id,
                        site_type=meet.site_type,
                        start=occurrence.start,
                        defaults={
                            'site_type': meet.site_type,
                            'site_id': meet.site_id,
                            'meet': meet,
                            'start': occurrence.start,
                            'finish': occurrence_end,
                            'infos': meet.infos,
                            'display_name': f'{meet.display_name} {occurrence.start.strftime("%Y/%m/%d,%H:%M %p %Z")}',
                        },
                    )  # don't update gatherings if exist since it may have customizations

                    if gathering_created:
                        number_created += 1

            results = {
                'number_created': number_created,
                'meet_slug': meet.slug,
                'begin': meet.start if meet.start > begin_time else begin_time,
                'end': meet.finish if meet.finish < end_time else end_time,
                'explain': "begin&end dates maybe replaced by Event's default dates."
            }

        else:
            results = {
                'number_created': number_created,
                'meet_slug': meet_slug,
                'begin': begin,
                'end': end,
                'explain': 'meet or begin&end time invalid.',
            }

        return results
