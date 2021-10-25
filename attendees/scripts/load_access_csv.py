import csv, os, pytz, re
from datetime import datetime, timedelta
from itertools import permutations
from glob import glob
from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from address.models import Locality, State, Address

from attendees.occasions.models import Assembly, Meet, Character, Gathering, Attendance
from attendees.persons.models import Utility, GenderEnum, Family, Relation, Attendee, FamilyAttendee, \
    Relationship, Registration, Attending, AttendingMeet, Past, Category
from attendees.users.admin import User
from attendees.whereabouts.models import Place, Division


def import_household_people_address(
        household_csv,
        people_csv,
        address_csv,
        division1_slug,
        division2_slug,
        division3_slug,
        data_assembly_slug,
        member_meet_slug,
        directory_meet_slug,
        baptized_meet_slug,
        # member_character_slug,
        # directory_character_slug,
        roaster_meet_slug,
        believer_meet_slug,
        # data_general_character_slug,
        # data_baptisee_character_slug,
    ):
    """
    Entry function of entire importer, it execute importers in sequence and print out results.
    :param household_csv: an existing file object of household with headers, from MS Access
    :param people_csv: an existing file object of household with headers, from MS Access
    :param address_csv: an existing file object of household with headers, from MS Access
    :param division1_slug: key of division 1  # ch
    :param division2_slug: key of division 2  # en
    :param division3_slug: key of division 3  # kid
    :param data_assembly_slug: key of data_assembly
    :param member_meet_slug: key of member_gathering
    :param directory_meet_slug: key of directory_gathering
    :param baptized_meet_slug: key of baptized_meet_slug
    :param roaster_meet_slug: key of roaster_meet_slug
    :param believer_meet_slug: key of believer_meet_slug
    :return: None, but print out importing status and write to Attendees db (create or update)
    """
    if User.objects.count() < 1:
        raise Exception("\n\nSorry, no user exits, did superuser created?")
    california = State.objects.filter(code='CA').first()
    if not california:
        raise Exception("\n\nSorry, California not imported, did db_seed.json loaded?")

    print("\n\n\nStarting import_household_people_address ...\n\n")
    households = csv.DictReader(household_csv)
    peoples = csv.DictReader(people_csv)
    addresses = csv.DictReader(address_csv)

    try:
        initial_time = datetime.utcnow()
        initial_contact_count = Place.objects.count()
        initial_family_count = Family.objects.count()
        initial_attendee_count = Attendee.objects.count()
        initial_relationship_count = Relationship.objects.count()
        upserted_address_count = import_addresses(addresses, california, division1_slug)
        upserted_household_id_count = import_households(households, division1_slug, division2_slug)
        upserted_attendee_count, photo_import_results = import_attendees(peoples, division3_slug, data_assembly_slug, member_meet_slug, baptized_meet_slug, roaster_meet_slug, believer_meet_slug)

        if upserted_address_count and upserted_household_id_count and upserted_attendee_count:
            upserted_relationship_count = reprocess_directory_emails_and_family_roles(data_assembly_slug, directory_meet_slug)
            print("\n\nProcessing results of importing/updating Access export csv files:\n")
            print('Number of address successfully imported/updated: ', upserted_address_count)
            print('Initial contact count: ', initial_contact_count, '. final contact count: ', Place.objects.count(), end="\n")

            print('Number of households successfully imported/updated: ', upserted_household_id_count)
            print('Initial family count: ', initial_family_count, '. final family count: ', Family.objects.count(), end="\n")

            place_with_family_count = Place.objects.filter(content_type=ContentType.objects.get_for_model(Family)).count()
            print('Number of place(address) successfully associated with family (originally 0): ', place_with_family_count)

            print('Number of people successfully imported/updated: ', upserted_attendee_count)
            print('Initial attendee count: ', initial_attendee_count, '. final attendee count: ', Attendee.objects.count(), end="\n")

            print('Number of relationship successfully imported/updated: ', upserted_relationship_count)
            print('Initial relationship count: ', initial_relationship_count, '. final relationship count: ', Relationship.objects.count(), end="\n")

            number_of_attendees_with_photo_assigned = len(photo_import_results)
            attendees_missing_photos = list(filter(None.__ne__, photo_import_results))
            print("\nPhoto import results: Out of ", number_of_attendees_with_photo_assigned, ' attendees assigned with photos, ', len(attendees_missing_photos), " were missing photo files:\n", *attendees_missing_photos)

            time_taken = (datetime.utcnow() - initial_time).total_seconds()
            print('Importing/updating Access CSV is now done, seconds taken: ', time_taken)
            print('Please manually fix the address not in USA!')
        else:
            print('Importing/updating address or household or attendee error, result count does not exist!')
    except Exception as e:
        print('Cannot proceed import_household_people_address, reason: ', e)

    pass


# Todo: Add created by notes in every instance in notes/infos
def import_addresses(addresses, california, division1_slug):
    """
    Importer of addresses from MS Access.
    :param addresses: file content of address accessible by headers, from MS Access
    :param california: Californis is the default state
    :return: successfully processed address count, also print out importing status and write to Attendees db (create or update)
    """

    print("\n\nRunning import_addresses:\n")
    successfully_processed_count = 0  # addresses.line_num always advances despite of processing success
    address_content_type = ContentType.objects.get_for_model(Address)  # ContentType.objects.get(model='address')
    organization = Division.objects.get(slug=division1_slug).organization
    for address_dict in addresses:
        try:
            print('.', end='')
            address_id = Utility.presence(address_dict.get('AddressID'))  # str
            state = Utility.presence(address_dict.get('State'))
            street = Utility.presence(address_dict.get('Street'))
            city = Utility.presence(address_dict.get('City'))
            zip_code = Utility.presence(address_dict.get('Zip'))
            if address_id and street and state == california.code:
                # locality, locality_created = Locality.objects.update_or_create(
                #     name=city,
                #     postal_code=zip_code or '',  # Locality.postal_code allow blank but not null
                #     state=california
                # )

                possible_extras = re.findall('((?i)(apt|unit|#| \D{1}\d+).+)$', street)  # Get extra info such as Apt#
                address_extra = possible_extras[0][0].strip() if possible_extras else ''
                street_strs = street.replace(address_extra, '').strip().strip(',').split(' ')

                contact_values = {
                    'address': {
                        'street_number': street_strs[0],
                        'route': ' '.join(street_strs[1:]),
                        'type': 'street',
                        'extra': Utility.presence(address_extra),
                        'locality': Utility.presence(address_dict.get('City')),
                        'postal_code': Utility.presence(address_dict.get('Zip')) or '',
                        'state': california.name,
                        'state_code': california.code,
                        'country': 'USA',
                        'country_code': 'US',
                        'raw': f"{street}, {city}, {state} {zip_code}",
                    },
                    'organization': organization,
                    'infos': {
                        **Utility.default_infos(),
                        'access_address_id': address_id,
                        'access_address_values': address_dict,
                    }
                }
                existing_places = Place.objects.filter(infos__access_address_id=address_id)  # multiple households can share an address

                if existing_places:
                    for place in existing_places:
                        place.infos = contact_values.get('infos')
                        address = place.address
                        address.street_number = contact_values.get('address', {}).get('street_number')
                        address.route = contact_values.get('address', {}).get('route')
                        address.raw = contact_values.get('address', {}).get('raw')

                        potential_new_local = Locality.objects.filter(postal_code=contact_values.get('address', {}).get('postal_code'), name=contact_values.get('address', {}).get('locality')).first()
                        if potential_new_local:
                            address.locality = potential_new_local

                        address.save()
                        place.save()
                else:
                    Place.objects.update_or_create(
                        infos__access_address_id=address_id,  # str
                        defaults={
                            **contact_values,
                            'content_type': address_content_type,
                            'object_id': str(address_id),  # will update later.  Remember some address are duplicated
                        }
                    )
            else:
                print('Is the address completed or in California? address not good for processing: ', address_dict)
            successfully_processed_count += 1

        except Exception as e:
            print('While importing/updating address: ', address_dict)
            print('An error occurred and cannot proceed import_addresses(), reason: ', e)
    print('done!')
    return successfully_processed_count


def import_households(households, division1_slug, division2_slug):
    """
    Importer of households from MS Access, also update display name and telephone number of Place.
    :param households: file content of households accessible by headers, from MS Access
    :param division1_slug: slug of division 1  # ch
    :param division2_slug: slug of division 2  # en
    :return: successfully processed family count, also print out importing status and write FamilyAddress to Attendees db (create or update)
    """
    default_division = Division.objects.first()
    division1 = Division.objects.get(slug=division1_slug)
    division2 = Division.objects.get(slug=division2_slug)
    division_converter = {
        'CH': division1,
        'EN': division2,
    }
    family_content_type = ContentType.objects.get_for_model(Family)
    print("\n\nRunning import_households:\n")
    successfully_processed_count = 0  # households.line_num always advances despite of processing success
    pdt = pytz.timezone('America/Los_Angeles')
    long_time_ago = pdt.localize(datetime(1800, 1, 1), is_dst=None)
    for index, household in enumerate(households, start=1):
        try:
            print('.', end='')
            household_id = Utility.presence(household.get('HouseholdID'))
            address_id = Utility.presence(household.get('AddressID'))  # str
            display_name = Utility.presence(household.get('HousholdLN', '') + ' ' + household.get('HousholdFN', '') + ' ' + household.get('SpouseFN', '')) or 'household_id: ' + household_id
            congregation = Utility.presence(household.get('Congregation'))

            if household_id:
                household_values = {
                    'created': long_time_ago + timedelta(index),  # bypass Todo: 20210516 order by attendee's family attendee display_order
                    'display_name': display_name,
                    'division': default_division,
                    'infos': {
                        'access_household_id': household_id,
                        'access_household_values': household,
                        'last_update': Utility.presence(household.get('LastUpdate')),
                        'contacts': {},
                    }
                }

                if congregation:
                    division = division_converter.get(congregation)
                    if division:
                        household_values['division'] = division

                family, family_created = Family.objects.update_or_create(
                    infos__access_household_id=household_id,
                    defaults=household_values
                )

                if address_id:
                    phone1 = Utility.presence(household.get('HouseholdPhone'))
                    phone2 = Utility.presence(household.get('HouseholdFax'))
                    # old_contact = Place.objects.filter(infos__access_address_id=address_id).first()
                    # address = old_contact.address if old_contact else None
                    saved_place = family.places.first() or Place.objects.filter(infos__access_address_id=address_id).first()

                    if saved_place:
                        potential_new_place_id = None

                        if saved_place.subject == family or saved_place.content_type != family_content_type:
                            potential_new_place_id = saved_place.id
                        address = saved_place.address

                        if address and not address.name:
                            full_address_name = display_name + ' family: ' + address.raw
                            address.name = display_name
                            address.raw = str(family.id)
                            address.formatted = full_address_name
                            address.save()

                        Place.objects.update_or_create(
                            id=potential_new_place_id,  # infos__access_address_id=address_id,  # multiple households could share the same address
                            # address=address,
                            defaults={
                                'address': address,
                                'display_name':  display_name,
                                'content_type': family_content_type,
                                'object_id': family.id,
                                'infos': {
                                    'access_address_id': address_id,  # str
                                    'contacts': {
                                        'phone1': add_int_code(phone1),  # Todo: check if repeating run adding extra country code such as +1+1+1-510-123-4567
                                        'phone2': add_int_code(phone2),  # Todo: need to remove contacts from Place since it's across organizations
                                    },
                                    'fixed': {}
                                },
                            }
                        )
            successfully_processed_count += 1

        except Exception as e:
            print('While importing/updating household: ', household)
            print('An error occurred and cannot proceed import_households, reason: ', e)
    print('done!')
    return successfully_processed_count


def import_attendees(peoples, division3_slug, data_assembly_slug, member_meet_slug, baptized_meet_slug, roaster_meet_slug, believer_meet_slug):
    """
    Importer of each people from MS Access.
    :param peoples: file content of people accessible by headers, from MS Access
    :param division3_slug: key of division 3  # kid
    :param data_assembly_slug: key of data_assembly
    :param member_meet_slug: key of member_meet
    :param baptized_meet_slug: key of baptized_meet_slug
    :param roaster_meet_slug: key of roaster_meet_slug
    :param believer_meet_slug: key of believer_meet_slug
    :return: successfully processed attendee count, also print out importing status and write Photo&FamilyAttendee to Attendees db (create or update)
    """
    gender_converter = {
        'F': GenderEnum.FEMALE,
        'M': GenderEnum.MALE,
    }

    progression_converter = {
        'Christian': 'christian',
        'Member': 'cfcc_member',
        'MemberDate': 'member_since',
        'FirstDate': 'visit_since',
        'BapDate': 'baptized_since',
        'BapLocation': 'baptism_location',
        'Group': 'language_group',
        'Active': 'active',
    }

    family_to_attendee_infos_converter = {
        'AttendenceCount': 'attendance_count',
        'FlyerMailing': 'flyer_mailing',
        'CardMailing': 'card_mailing',
        'UpdateDir': 'update_directory',
        'PrintDir': 'print_directory',
        'LastUpdate': 'household_last_update',
        '海沃之友': 'hayward_friend',
    }

    print("\n\nRunning import_attendees: \n")
    default_division = Division.objects.first()
    division3 = Division.objects.get(slug=division3_slug)  # kid
    data_assembly = Assembly.objects.get(slug=data_assembly_slug)
    visitor_meet = Meet.objects.get(pk=0)
    member_meet = Meet.objects.get(slug=member_meet_slug)
    member_gathering = Gathering.objects.filter(meet=member_meet).last()
    roaster_meet = Meet.objects.get(slug=roaster_meet_slug)
    roaster_gathering = Gathering.objects.filter(meet=roaster_meet).last()
    # pdt = pytz.timezone('America/Los_Angeles')
    member_character = member_meet.major_character
    roaster_character = roaster_meet.major_character
    attendee_content_type = ContentType.objects.get_for_model(Attendee)
    baptized_meet = Meet.objects.get(slug=baptized_meet_slug)
    baptized_category = Category.objects.filter(type='status', display_name='baptized').first()
    baptisee_character = baptized_meet.major_character
    believer_category = Category.objects.filter(type='status', display_name='receive').first()
    believer_meet = Meet.objects.get(slug=believer_meet_slug)
    believer_character = believer_meet.major_character
    successfully_processed_count = 0  # Somehow peoples.line_num incorrect, maybe csv file come with extra new lines.
    photo_import_results = []
    for people in peoples:
        try:
            print('.', end='')
            first_name = Utility.presence(people.get('FirstName'))
            last_name = Utility.presence(people.get('LastName'))
            birth_date = Utility.presence(people.get('BirthDate'))
            name2 = Utility.presence(people.get('ChineseName'))
            household_id = Utility.presence(people.get('HouseholdID'))
            household_role = Utility.presence(people.get('HouseholdRole'))

            if household_id and (first_name or last_name):
                phones = [Utility.presence(people.get('WorkPhone')), Utility.presence(people.get('CellPhone'))]
                email = Utility.presence(people.get('E-mail'))
                if email:
                    if '@' not in email:  # some phone number are accidentally in email column
                        phones = [email] + phones
                        email = None
                phone1, phone2 = return_two_phones(phones)

                contacts = {
                            'email1': email,
                            'email2': None,
                            'phone1': add_int_code(phone1),
                            'phone2': add_int_code(phone2),
                            }
                attendee_values = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'first_name2': None,
                    'last_name2': None,
                    'gender': gender_converter.get(Utility.presence(people.get('Sex', '').upper()), GenderEnum.UNSPECIFIED).name,
                    'progressions': {attendee_header: Utility.boolean_or_datetext_or_original(people.get(access_header)) for (access_header, attendee_header) in progression_converter.items() if Utility.presence(people.get(access_header)) is not None},
                    'infos': {
                        **Utility.attendee_infos(),
                        'fixed': {
                            'access_people_household_id': household_id,
                            'access_people_values': people,
                        },
                        'contacts': contacts,
                        'names': {},
                        'created_reason': 'CFCCH member/directory registration from importer',
                    }
                }

                if birth_date:
                    try:
                        formatting_birthdate = Utility.boolean_or_datetext_or_original(birth_date)
                        attendee_values['actual_birthday'] = datetime.strptime(formatting_birthdate, '%Y-%m-%d').date()
                    except ValueError as ve:
                        print("\nImport_attendees error on BirthDate of people: ", people, '. Reason: ', ve, ". This birthday will be skipped. Other columns of this people will still be saved. Continuing. \n")

                if name2:  # assume longest last name is 2 characters
                    break_position = -2 if len(name2) > 2 else -1
                    attendee_values['first_name2'] = name2[break_position:]
                    attendee_values['last_name2'] = name2[:break_position]

                query_values = {
                    'first_name': attendee_values['first_name'],
                    'last_name': attendee_values['last_name'],
                    'first_name2': attendee_values['first_name2'],
                    'last_name2': attendee_values['last_name2'],
                    'infos__fixed__access_people_household_id': household_id,
                }

                attendee, attendee_created = Attendee.objects.update_or_create(
                    **{k: v for (k, v) in query_values.items() if v is not None},
                    defaults={k: v for (k, v) in attendee_values.items() if v is not None}
                )

                photo_import_results.append(update_attendee_photo(attendee, Utility.presence(people.get('Photo'))))
                update_attendee_membership(baptized_meet, baptized_category, attendee_content_type, attendee, data_assembly, member_meet, member_character, member_gathering, baptisee_character, believer_meet, believer_character, believer_category)

                if household_role:   # filling temporary family roles
                    family = Family.objects.filter(infos__access_household_id=household_id).first()
                    if family:       # there are some missing records in the access data
                        if household_role == 'A(Self)':
                            relation = Relation.objects.get(title='self')
                            display_order = 0
                            attendee.division = family.division or default_division
                        elif household_role == 'B(Spouse)':
                            relation = Relation.objects.get(
                                title__in=['spouse', 'husband', 'wife'],
                                gender=attendee.gender,
                            )  # There are wives mislabelled as 'Male' in Access data
                            display_order = 1
                            attendee.division = family.division or default_division
                        else:
                            relation = Relation.objects.get(
                                title__in=['child', 'son', 'daughter'],
                                gender=attendee.gender,
                            )
                            if attendee.age() and attendee.age() < 11:  # k-5 to kid, should > 10 to EN?
                                attendee.division = division3
                            display_order = 10

                        some_household_values = {attendee_header: Utility.boolean_or_datetext_or_original(family.infos.get('access_household_values', {}).get(access_header)) for (access_header, attendee_header) in family_to_attendee_infos_converter.items() if Utility.presence(family.infos.get('access_household_values', {}).get(access_header)) is not None}
                        attendee.infos = {'fixed': {**attendee.infos.get('fixed', {}), **some_household_values}, 'contacts': contacts, 'names': attendee.infos.get('names', {})}

                        attendee.save()
                        FamilyAttendee.objects.update_or_create(
                            family=family,
                            attendee=attendee,
                            defaults={
                                'display_order': display_order,
                                'role': relation,
                                # 'start': '1850-01-01',
                            }
                        )
                        #
                        # address_id = family.infos.get('access_household_values', {}).get('AddressID', 'missing')
                        # family_place = Place.objects.filter(infos__access_address_id=address_id).first()
                        # if family_place:
                        #     Place.objects.update_or_create(
                        #         address=family_place.address,
                        #         content_type=attendee_content_type,
                        #         object_id=attendee.id,
                        #         address_extra=family_place.address_extra,
                        #         defaults={
                        #             'address': family_place.address,
                        #             'content_type': attendee_content_type,
                        #             'object_id': attendee.id,
                        #             'display_name': 'main',
                        #             'display_order': 0,
                        #             'address_extra': family_place.address_extra,
                        #             'infos': {
                        #                 'contacts': {},
                        #                 'fixed': {},
                        #             },
                        #         }
                        #     )  # don't add infos__access_address_id so future query will only get one at family level
                    else:
                        print("\nBad data, cannot find the household id: ", household_id, ' for people: ', people, " Other columns of this people will still be saved. Continuing. \n")

                update_attendee_worship_roaster(attendee, data_assembly, visitor_meet, roaster_meet, roaster_character, roaster_gathering)
            else:
                print('There is no household_id or first/lastname of the people: ', people)
            successfully_processed_count += 1

        except Exception as e:
            print("\nWhile importing/updating people: ", people)
            print('Cannot save import_attendees, reason: ', e)
    print('done!')
    return successfully_processed_count, photo_import_results  # list(filter(None.__ne__, photo_import_results))


def reprocess_directory_emails_and_family_roles(data_assembly_slug, directory_meet_slug):
    """
    Reprocess extra data (email/relationship) from FamilyAttendee, also do data correction of Role
    :param data_assembly_slug: key of data_assembly
    :param directory_meet_slug: key of directory_gathering
    :return: successfully processed relation count, also print out importing status and write to Attendees db (create or update)
    """
    print("\n\nRunning reprocess_family_roles: \n")
    husband_role = Relation.objects.get(
        title='husband',
        gender=GenderEnum.MALE.name,
    )

    wife_role = Relation.objects.get(
        title='wife',
        gender=GenderEnum.FEMALE.name,
    )
    data_assembly = Assembly.objects.get(slug=data_assembly_slug)
    directory_meet = Meet.objects.get(slug=directory_meet_slug)
    directory_gathering = Gathering.objects.filter(meet=directory_meet).last()
    directory_character = directory_meet.major_character
    imported_families = Family.objects.filter(infos__access_household_id__isnull=False).order_by('created')  # excludes seed data
    successfully_processed_count = 0
    for family in imported_families:
        try:
            print('.', end='')
            children = family.attendees.filter(familyattendee__role__title__in=['child', 'son', 'daughter']).all()
            parents = family.attendees.filter(familyattendee__role__title__in=['self', 'spouse', 'husband', 'wife']).order_by().all()  # order_by() is critical for values_list('gender').distinct() later
            families_address = family.places.first() # families_address = Address.objects.filter(pk=family.addresses.first().id).first()
            potential_primary_phone = family.infos.get('access_household_values', {}).get('HouseholdPhone')
            if len(parents) > 1:  # family role modification skipped for singles
                potential_secondary_phone = family.infos.get('access_household_values', {}).get('HouseholdFax')
                if len(parents.values_list('gender', flat=True).distinct()) < 2:
                    print("\n Parents genders are mislabelled, trying to reassign them: ", parents)

                    if set(['Chloris', 'Yvone']) & set(parents.values_list('first_name', flat=True)):  # these two are special cases in Access data
                        wife, husband = parents.order_by('created')
                    else:
                        husband, wife = parents.order_by('created')

                    husband.gender = GenderEnum.MALE.name
                    husband.save()
                    husband_familyattendee = husband.familyattendee_set.first()
                    husband_familyattendee.role=husband_role
                    husband_familyattendee.save()

                    wife.gender = GenderEnum.FEMALE.name
                    wife.save()
                    wife_familyattendee = wife.familyattendee_set.first()
                    wife_familyattendee.role = wife_role
                    wife_familyattendee.save()
                    print('After reassigning, now husband is: ', husband, '. And wife is: ', wife, '. Continuing. ')

                unspecified_househead = family.attendees.filter(familyattendee__role__title='self').first()
                # Todo: even some househeads are alone, there are some cases of bachelor/widow !!
                if unspecified_househead:
                    househead_role = Relation.objects.get(
                        title__in=['husband', 'wife'],
                        gender=unspecified_househead.gender,
                    )
                    FamilyAttendee.objects.update_or_create(
                        family=family,
                        attendee=unspecified_househead,
                        defaults={'display_order': 0, 'role': househead_role}
                    )
                    save_two_phones(unspecified_househead, potential_primary_phone)

                husband = family.attendees.filter(familyattendee__role__title='husband').order_by('created').first()
                wife = family.attendees.filter(familyattendee__role__title='wife').order_by('created').first()

                save_two_phones(husband, potential_primary_phone)
                save_two_phones(wife, potential_secondary_phone)

                hushand_email = husband.infos.get('fixed', {}).get('access_people_values', {}).get('E-mail')
                wife_email = wife.infos.get('fixed', {}).get('access_people_values', {}).get('E-mail')
                family.infos['contacts']['email1'] = Utility.presence(hushand_email)
                family.infos['contacts']['email2'] = Utility.presence(wife_email)
                family.save()

                Relationship.objects.update_or_create(
                    from_attendee=wife,
                    to_attendee=husband,
                    relation=husband_role,
                    defaults={
                        'in_family': family,
                        'emergency_contact': husband_role.emergency_contact,
                        'scheduler': husband_role.scheduler,
                        # 'finish': Utility.forever(),
                        'infos': Utility.relationship_infos(),
                        #{
                        #    'show_secret': {},
                       # },
                    }
                )

                Relationship.objects.update_or_create(
                    from_attendee=husband,
                    to_attendee=wife,
                    relation=wife_role,
                    defaults={
                        'in_family': family,
                        'emergency_contact': wife_role.emergency_contact,
                        'scheduler': wife_role.scheduler,
                        # 'finish': Utility.forever(),
                        'infos': Utility.relationship_infos(),
                        #{
                        #    'show_secret': {},
                        #},
                    }
                )
                successfully_processed_count += 2

            else:
                househead_single = parents.first()
                if househead_single:  # update gender by family role since some access_family role records are incorrect.
                    original_household_role = househead_single.infos.get('fixed', {}).get('access_people_values', {}).get('HouseholdRole')
                    if original_household_role == 'B(Spouse)':  # 'Chloris', 'Yvone' are parents > 1
                        househead_single.gender = GenderEnum.FEMALE.name
                        househead_single.save()
                        family_attendee = househead_single.familyattendee_set.first()
                        family_attendee.role = wife_role
                        family_attendee.save()

                    self_email = househead_single.infos.get('fixed', {}).get('access_people_values', {}).get('E-mail')
                    family.infos['contacts']['email1'] = Utility.presence(self_email)
                    family.save()
                    save_two_phones(househead_single, potential_primary_phone)

                else:
                    if Attendee.objects.filter(infos__fixed__access_people_household_id=family.infos['access_household_id']):
                        print("\nSomehow there's no one in families parents or househead_single (orphan?), for family ", family, '. families_address: ', families_address, '. parents: ', parents, '. household_id: ', family.infos['access_household_id'], '. family.id: ', family.id, '. Continuing to next record.')
                    else:
                        pass  # skipping since there is no such people with the household id in the original access data.

            siblings = permutations(children, 2)
            for (from_child, to_child) in siblings:
                househead_role = Relation.objects.get(
                    title__in=['brother', 'sister', 'sibling'],
                    gender=to_child.gender,
                )
                Relationship.objects.update_or_create(
                    from_attendee=from_child,
                    to_attendee=to_child,
                    relation=househead_role,
                    defaults={
                                'in_family': family,
                                'emergency_contact': False,
                                'scheduler': False,
                                # 'finish': Utility.forever(),
                                'infos': Utility.relationship_infos(),
                                #{
                                #    'show_secret': {},
                                #},
                             }
                )
                successfully_processed_count += 1

            for parent in family.attendees.filter(familyattendee__role__title__in=['self', 'spouse', 'husband', 'wife']).order_by().all():  # reload to get updated parent gender
                parent_role = Relation.objects.get(
                    title__in=['father', 'mother', 'parent'],
                    gender=parent.gender,
                )
                for child in children:
                    child_role = Relation.objects.get(
                        title__in=['child', 'son', 'daughter'],
                        gender=child.gender,
                    )
                    Relationship.objects.update_or_create(
                        from_attendee=parent,
                        to_attendee=child,
                        relation=child_role,
                        defaults={
                            'in_family': family,
                            'emergency_contact': child_role.emergency_contact,
                            'scheduler': child_role.scheduler,
                            # 'finish': Utility.forever(),
                            'infos': Utility.relationship_infos(),
                            #{
                            #    'show_secret': {},
                            #},
                        }
                    )

                    Relationship.objects.update_or_create(
                        from_attendee=child,
                        to_attendee=parent,
                        relation=parent_role,
                        defaults={
                            'in_family': family,
                            'emergency_contact': parent_role.emergency_contact,
                            'scheduler': parent_role.scheduler,
                            # 'finish': Utility.forever(),
                            'infos': Utility.relationship_infos(),
                            #{
                            #    'show_secret': {},
                            #},
                        }
                    )
                    successfully_processed_count += 2

            update_directory_data(data_assembly, family, directory_meet, directory_character, directory_gathering)

        except Exception as e:
            print("\nWhile importing/updating relationship for family: ", family)
            print('Cannot save relationship or update_directory_data, reason: ', e)
    print('done!')
    return successfully_processed_count


def update_attendee_worship_roaster(attendee, data_assembly, visitor_meet, roaster_meet, general_character, roaster_gathering):
    pdt = pytz.timezone('America/Los_Angeles')
    access_household_id = attendee.infos.get('fixed', {}).get('access_people_household_id')
    data_registration, data_registration_created = Registration.objects.update_or_create(
        assembly=data_assembly,
        registrant=attendee,
        defaults={
            'registrant': attendee,  # admin/secretary may change for future members.
            'assembly': data_assembly,
            'infos': {
                'access_household_id': access_household_id,
                'created_reason': 'CFCCH member/directory registration from importer',
            }
        }
    )

    data_attending, data_attending_created = Attending.objects.update_or_create(
        attendee=attendee,
        registration=data_registration,
        defaults={
            'registration': data_registration,
            'attendee': attendee,
            'infos': {
                'created_reason': 'CFCCH member/directory registration from importer',
            }
        }
    )

    AttendingMeet.objects.update_or_create(
        attending=data_attending,
        meet=visitor_meet,
        defaults={
            'character': general_character,
            'category': 'importer',
            'start': visitor_meet.start,
            'finish': visitor_meet.finish,
        },
    )

    if attendee.infos.get('fixed', {}).get('attendance_count'):
        AttendingMeet.objects.update_or_create(
            attending=data_attending,
            meet=roaster_meet,
            defaults={
                'character': general_character,
                'category': 'importer',
                'start': roaster_meet.start,
                'finish': datetime.now(pdt) + timedelta(365),  # whoever don't attend for a year won't be counted anymore
            },
        )

        Attendance.objects.update_or_create(
            gathering=roaster_gathering,
            attending=data_attending,
            character=general_character,
            team=None,
            defaults={
                'gathering': roaster_gathering,
                'attending': data_attending,
                'character': general_character,
                'team': None,
                'start': roaster_gathering.start,
                'finish': roaster_gathering.finish,
                'infos': {
                    'access_household_id': access_household_id,
                    'created_reason': 'CFCCH member/directory registration from importer',
                },
            }
        )


def update_attendee_membership(baptized_meet, baptized_category, attendee_content_type, attendee, data_assembly, member_meet, member_character, member_gathering, baptisee_character, believer_meet, believer_character, believer_category):
    if attendee.progressions.get('cfcc_member'):
        access_household_id = attendee.infos.get('fixed', {}).get('access_people_household_id')
        data_registration, data_registration_created = Registration.objects.update_or_create(
            assembly=data_assembly,
            registrant=attendee,
            defaults={
                'registrant': attendee,  # admin/secretary may change for future members.
                'assembly': data_assembly,
                'infos': {
                    'access_household_id': access_household_id,
                    'created_reason': 'CFCCH member/directory registration from importer',
                }
            }
        )

        data_attending, data_attending_created = Attending.objects.update_or_create(
            attendee=attendee,
            registration=data_registration,
            defaults={
                'registration': data_registration,
                'attendee': attendee,
                'infos': {
                    'access_household_id': access_household_id,
                    'created_reason': 'CFCCH member/directory registration from importer',
                }
            }
        )

        member_since_or_now = Utility.parsedate_or_now(attendee.progressions.get('member_since'))
        member_attending_meet_default = {
            'attending': data_attending,
            'meet': member_meet,
            'character': member_character,
            'category': 'active',  # member category has to be active or inactive
            'start': member_since_or_now,
            'finish': member_meet.finish,
        }

        AttendingMeet.objects.update_or_create(
            attending=data_attending,
            meet=member_meet,
            defaults=member_attending_meet_default,
        )

        Attendance.objects.update_or_create(
            gathering=member_gathering,
            attending=data_attending,
            character=member_character,
            team=None,
            defaults={
                'gathering': member_gathering,
                'attending': data_attending,
                'character': member_character,
                'team': None,
                'category': 'active',  # membership can be inactive temporarily
                'start': member_attending_meet_default['start'],
                'finish': member_gathering.finish,
                'infos': {
                    'access_household_id': access_household_id,
                    'created_reason': 'CFCCH member/directory registration from importer',
                },
            }
        )

        member_since_text = Utility.presence(attendee.progressions.get('member_since'))
        member_since_reason = ', member since ' + member_since_text if member_since_text else ''
        Past.objects.update_or_create(
            organization=data_assembly.division.organization,
            content_type=attendee_content_type,
            object_id=attendee.id,
            category=believer_category,
            display_name="會員已信主 member's believer",
            when=None,  # can't find the exact receive date just by membership
            infos={
                **Utility.relationship_infos(),
                'comment': 'CFCCH membership from importer' + member_since_reason,
            },
        )
        Past.objects.update_or_create(
            organization=data_assembly.division.organization,
            content_type=attendee_content_type,
            object_id=attendee.id,
            category=baptized_category,
            display_name="會員已受浸 member's baptized",
            when=None,  # can't find the exact baptism date just by membership
            infos={
                **Utility.relationship_infos(),
                'comment': 'CFCCH membership from importer' + member_since_reason,
            },
        )

        AttendingMeet.objects.update_or_create(
            attending=data_attending,
            meet=believer_meet,
            defaults={
                'attending': data_attending,
                'meet': believer_meet,
                'character': believer_character,
                'category': 'importer',
                'start': member_since_or_now,
                'finish': believer_meet.finish,
            },
        )

        AttendingMeet.objects.update_or_create(
            attending=data_attending,
            meet=baptized_meet,
            defaults={
                'attending': data_attending,
                'meet': baptized_meet,
                'character': baptisee_character,
                'category': 'importer',
                'start': member_since_or_now,
                'finish': baptized_meet.finish,
            },
        )


def update_directory_data(data_assembly, family, directory_meet, directory_character, directory_gathering):
    """
    update assembly and gathering for directory.
    :param data_assembly: data_assembly
    :param family: each family
    :param directory_meet: directory_meet
    :param directory_character: directory_character
    :param directory_gathering: directory_gathering
    :return: None, but print out importing status and write to Attendees db (create or update)
    """
    if family.infos.get('access_household_values', {}).get('PrintDir') == 'TRUE':
        access_household_id = family.infos.get('access_household_id')
        househead = family.attendees.order_by('familyattendee__display_order').first()

        if househead:
            data_registration, data_registration_created = Registration.objects.update_or_create(
                assembly=data_assembly,
                registrant=househead,
                defaults={
                    'registrant': househead,
                    'assembly': data_assembly,
                    'infos': {
                        'access_household_id': access_household_id,
                        'created_reason': 'CFCCH member/directory registration from importer',
                    }
                }
            )

            for family_member in family.attendees.all():
                directory_attending, directory_attending_created = Attending.objects.update_or_create(
                    registration=data_registration,
                    attendee=family_member,
                    defaults={
                        'registration': data_registration,
                        'attendee': family_member,
                        'infos': {
                            'access_household_id': access_household_id,
                            'created_reason': 'CFCCH member/directory registration from importer',
                        }
                    }
                )

                AttendingMeet.objects.update_or_create(
                    attending=directory_attending,
                    meet=directory_meet,
                    defaults={
                        'attending': directory_attending,
                        'meet': directory_meet,
                        'character': directory_character,
                        'category': 'importer',
                        'start': directory_gathering.start,
                        'finish': directory_gathering.finish,
                    }
                )

                Attendance.objects.update_or_create(
                    gathering=directory_gathering,
                    attending=directory_attending,
                    character=directory_character,
                    team=None,
                    defaults={
                        'gathering': directory_gathering,
                        'attending': directory_attending,
                        'character': directory_character,
                        'team': None,
                        'start': directory_gathering.start,
                        'finish': directory_gathering.finish,
                        'infos': {
                            'access_household_id': access_household_id,
                            'created_reason': 'CFCCH member/directory registration from importer',
                        },
                    }
                )


def update_attendee_photo(attendee, photo_names):
    """
    search photo file and update photo for attendee (update/create).
    :param attendee: attendee
    :param photo_names: photo_names from MS Access data
    :return: Failure message, but write to Attendees db (create or update)
    """
    import_photo_success = False
    if photo_names:
        photo_infos={}
        for photo_filename in photo_names.split(';'):
            found_picture_files = glob('**/' + photo_filename, recursive=True)
            found_picture_file_name = found_picture_files[0] if len(found_picture_files) > 0 else None
            if found_picture_file_name:
                pathlib_file_name = Path(found_picture_file_name)
                file_modified_time = datetime.fromtimestamp(pathlib_file_name.stat().st_mtime)
                photo_infos[found_picture_file_name] = file_modified_time
        if bool(photo_infos):
            latest_file_name = max(photo_infos, key=photo_infos.get)
            picture_name = latest_file_name.split('/')[-1]
            image_file = File(file=open(latest_file_name, 'rb'), name=picture_name)

            if attendee.photo:
                old_file_path = attendee.photo.path
                attendee.photo.delete()
                if os.path.isfile(old_file_path):
                    os.remove(old_file_path)

            attendee.photo.save(picture_name, image_file, True)
            attendee.save()
            import_photo_success = True
    else:
        import_photo_success = None
    if import_photo_success or import_photo_success is None:
        return None  # import failure message
    else:
        return 'Attendee ' + str(attendee) + ' photo file(s) missing: ' + photo_names + "\n"


def return_two_phones(phones):
    cleaned_phones = list(set([re.sub("[^0-9\+]+", "", p) for p in phones if (p and not p.isspace())]))
    return (cleaned_phones + [None, None])[0:2]


def save_two_phones(attendee, phone):
    if phone:
        phone1, phone2 = return_two_phones([add_int_code(phone), attendee.infos.get('contacts', {}).get('phone1'), attendee.infos.get('contacts', {}).get('phone2')])
        attendee.infos['contacts'] = {
            'phone1': add_int_code(phone1),
            'phone2': add_int_code(phone2),
            'email1': attendee.infos.get('contacts', {}).get('email1'),
            'email2': attendee.infos.get('contacts', {}).get('email2'),
        }
        attendee.save()


def add_int_code(phone, default='+1'):
    if phone and not phone.isspace():
        if '+' in phone:
            return phone
        else:
            return default + phone
    else:
        return None

def check_all_headers():
    #households_headers = ['HouseholdID', 'HousholdLN', 'HousholdFN', 'SpouseFN', 'AddressID', 'HouseholdPhone', 'HouseholdFax', 'AttendenceCount', 'FlyerMailing', 'CardMailing', 'UpdateDir', 'PrintDir', 'LastUpdate', 'HouseholdNote', 'FirstDate', '海沃之友', 'Congregation']
    #peoples_headers = ['LastName', 'FirstName', 'NickName', 'ChineseName', 'Photo', 'Sex', 'Active', 'HouseholdID', 'HouseholdRole', 'E-mail', 'WorkPhone', 'WorkExtension', 'CellPhone', 'BirthDate', 'Skills', 'FirstDate', 'BapDate', 'BapLocation', 'Member', 'MemberDate', 'Fellowship', 'Group', 'LastContacted', 'AssignmentID', 'LastUpdated', 'PeopleNote', 'Christian']
    #addresses_headers = ['AddressID', 'Street', 'City', 'State', 'Zip', 'Country']
    pass


def run(
        household_csv_file,
        people_csv_file,
        address_csv_file,
        division1_slug,
        division2_slug,
        division3_slug,
        data_assembly_slug,
        member_meet_slug,
        directory_meet_slug,
        baptized_meet_slug,
        # member_character_slug,
        # directory_character_slug,
        roaster_meet_slug,
        # data_general_character_slug,
        # data_baptisee_character_slug,
        believer_meet_slug,
        *extras
    ):
    """
    An importer to import old MS Access db data, if same records founds in Attendees db, it will update.
    :param household_csv_file: a comma separated file of household with headers, from MS Access
    :param people_csv_file: a comma separated file of household with headers, from MS Access
    :param address_csv_file: a comma separated file of household with headers, from MS Access
    :param division1_slug: key of division 1  # ch
    :param division2_slug: key of division 2  # en
    :param division3_slug: key of division 3  # kid
    :param data_assembly_slug: key of data_assembly
    :param member_meet_slug: key of member_meet
    :param directory_meet_slug: key of directory_meet
    :param baptized_meet_slug: key of baptized_meet
    :param roaster_meet_slug: key of roaster_meet_slug
    :param believer_meet_slug: key of believer_meet_slug
    :param extras: optional other arguments
    :return: None, but write to Attendees db (create or update)
    """

    print("Running load_access_csv.py... with arguments: ")
    print("Reading household_csv_file: ", household_csv_file)
    print("Reading people_csv_file: ", people_csv_file)
    print("Reading address_csv_file: ", address_csv_file)
    print("Reading division1_slug: ", division1_slug)
    print("Reading division2_slug: ", division2_slug)
    print("Reading division3_slug: ", division3_slug)
    print("Reading data_assembly_slug: ", data_assembly_slug)
    print("Reading member_meet_slug: ", member_meet_slug)
    print("Reading directory_meet_slug: ", directory_meet_slug)
    # print("Reading member_character_slug: ", member_character_slug)
    # print("Reading directory_character_slug: ", directory_character_slug)
    print("Reading roaster_meet_slug: ", roaster_meet_slug)
    print("Reading believer_meet_slug: ", believer_meet_slug)
    print("Reading extras: ", extras)
    print("Divisions required for importing, running commands: docker-compose -f local.yml run django python manage.py runscript load_access_csv --script-args path/tp/household.csv path/to/people.csv path/to/address.csv division1_slug division2_slug division3_slug member_data_assembly_member_meet_slug directory_meet_slug member_character_slug directory_character_slug")

    if household_csv_file and people_csv_file and address_csv_file and division1_slug and division2_slug:
        with open(household_csv_file, mode='r', encoding='utf-8-sig') as household_csv, open(people_csv_file, mode='r', encoding='utf-8-sig') as people_csv, open(address_csv_file, mode='r', encoding='utf-8-sig') as address_csv:
            import_household_people_address(
                household_csv,
                people_csv,
                address_csv,
                division1_slug,
                division2_slug,
                division3_slug,
                data_assembly_slug,
                member_meet_slug,
                directory_meet_slug,
                baptized_meet_slug,
                # member_character_slug,
                # directory_character_slug,
                roaster_meet_slug,
                believer_meet_slug,
                # data_general_character_slug,
                # data_baptisee_character_slug,
            )
