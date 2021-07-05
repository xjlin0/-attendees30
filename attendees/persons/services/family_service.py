from attendees.persons.models import Relationship


class FamilyService:

    @staticmethod
    def destroy_with_associations(family, attendee):
        """
        No permission check.
        if family have more than one FamilyAttendees:
            only delete the FamilyAttendees, and reset non-blood Relationships. Places and Family still remained
        if family have only one FamilyAttendees (regardless which FamilyAttendees):
            delete family, places, FamilyAttendees and reset non-blood Relationships

        :param family: a family object
        :param attendee: an attendee object, whose name will be removed from family display_name
        :return: None
        """

        if family.familyattendee_set.count() < 2 and family.familyattendee_set.first() == attendee:
            Relationship.objects.filter(in_family=family.id, relation__consanguinity=False).delete()
            Relationship.objects.filter(in_family=family.id, relation__consanguinity=True).update(in_family=None)
            family.places.all().delete()
            family.familyattendee_set.all().delete()
            family.delete()

        else:
            family_name = family.display_name
            for attendee_name in attendee.all_names():
                family_name.replace(attendee_name, '')
            family.display_name = family_name
            family.save()
            Relationship.objects.filter(from_attendee=attendee, in_family=family.id, relation__consanguinity=False).delete()
            family.familyattendee_set.filter(attendee=attendee).delete()
