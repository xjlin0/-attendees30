from django.db.models import Q
from attendees.occasions.models import Gathering


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
    def batch_create(validated_data):
        print("hi 58 here is validated_data: "); print(validated_data)
        return 42
