import csv
from datetime import datetime
from itertools import permutations
from glob import glob
from pathlib import Path
from django.core.files import File

from attendees.persons.models import Utility, GenderEnum, Family, FamilyAddress, Relation, Attendee, FamilyAttendee, AttendeeAddress, Relationship
from attendees.whereabouts.models import Address, Division


def import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug, division3_slug):
    print("\n\n\nStarting import_household_people_address ...\n\n")
    households = csv.DictReader(household_csv)
    peoples = csv.DictReader(people_csv)
    addresses = csv.DictReader(address_csv)

    try:
        initial_time = datetime.utcnow()
        initial_address_count = Address.objects.count()
        initial_family_count = Family.objects.count()
        initial_attendee_count = Attendee.objects.count()
        initial_relationship_count = Relationship.objects.count()
        upserted_address_count = import_addresses(addresses)
        upserted_household_id_count = import_households(households, division1_slug, division2_slug)
        upserted_attendee_count = import_attendees(peoples, division3_slug)

        if upserted_address_count and upserted_household_id_count and upserted_attendee_count:
            upserted_relationship_count = reprocess_emails_and_family_roles()
            print("\n\nProcessing results of importing/updating Access export csv files:\n")
            print('Number of address successfully imported/updated: ', upserted_address_count)
            print('Initial address count: ', initial_address_count, '. final address count: ', Address.objects.count(), end="\n")

            print('Number of households successfully imported/updated: ', upserted_household_id_count)
            print('Initial family count: ', initial_family_count, '. final family count: ', Family.objects.count(), end="\n")

            print('Number of people successfully imported/updated: ', upserted_attendee_count)
            print('Initial attendee count: ', initial_attendee_count, '. final attendee count: ', Attendee.objects.count(), end="\n")

            print('Number of relationship successfully imported/updated: ', upserted_relationship_count)
            print('Initial relationship count: ', initial_relationship_count, '. final relationship count: ', Relationship.objects.count(), end="\n")

            time_taken = (datetime.utcnow() - initial_time).total_seconds()
            print('Importing/updating Access CSV is now done, seconds taken: ', time_taken)
        else:
            print('Importing/updating address or household or attendee error, result count does not exist!')
    except Exception as e:
        print('Cannot proceed import_household_people_address, reason: ', e)

    pass


def import_addresses(addresses):
    print("\n\nRunning import_addresses:\n")
    successfully_processed_count = 0  # addresses.line_num always advances despite of processing success
    for address in addresses:
        try:
            print('.', end='')
            address_id = Utility.presence(address.get('AddressID'))

            if address_id:
                address_values = {
                    'street1': Utility.presence(address.get('Street')),
                    'city': Utility.presence(address.get('City')),
                    'state': Utility.presence(address.get('State')),
                    'zip_code': Utility.presence(address.get('Zip')),
                    'country': Utility.presence(address.get('Country')),
                    'fields': {
                        'access_address_id': address_id,
                        'access_address_values': address,
                    }
                }
                Address.objects.update_or_create(
                    fields__access_address_id=address_id,
                    defaults=address_values
                )
            successfully_processed_count += 1

        except Exception as e:
            print('While importing/updating address: ', address)
            print('An error occurred and cannot proceed import_addresses(), reason: ', e)
    print('done!')
    return successfully_processed_count


def import_households(households, division1_slug, division2_slug):
    division1 = Division.objects.get(slug=division1_slug)
    division2 = Division.objects.get(slug=division2_slug)
    division_converter = {
        'CH': division1,
        'EN': division2,
    }
    print("\n\nRunning import_households:\n")
    successfully_processed_count = 0  # households.line_num always advances despite of processing success
    for household in households:
        try:
            print('.', end='')
            household_id = Utility.presence(household.get('HouseholdID'))
            address_id = Utility.presence(household.get('AddressID'))
            display_name = Utility.presence(household.get('HousholdLN', '') + ' ' + household.get('HousholdFN', '') + ' ' + household.get('SpouseFN', '')) or 'household_id: ' + household_id
            congregation = Utility.presence(household.get('Congregation'))

            if household_id:
                household_values = {
                    'display_name': display_name,
                    'infos': {
                        'access_household_id': household_id,
                        'access_household_values': household,
                        'last_update': Utility.presence(household.get('LastUpdate')),
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
                    address, address_created = Address.objects.update_or_create(
                        fields__access_address_id=address_id,
                        defaults={
                            'display_name':  display_name,
                            'phone1': Utility.presence(household.get('HouseholdPhone')),
                            'phone2': Utility.presence(household.get('HouseholdFax')),
                        }
                    )
                    FamilyAddress.objects.update_or_create(
                        family=family,
                        address=address
                    )
            successfully_processed_count += 1

        except Exception as e:
            print('While importing/updating household: ', household)
            print('An error occurred and cannot proceed import_households, reason: ', e)
    print('done!')
    return successfully_processed_count


def import_attendees(peoples, division3_slug):
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
    print("\n\nRunning import_attendees: \n")
    division3 = Division.objects.get(slug=division3_slug)
    successfully_processed_count = 0  # Somehow peoples.line_num incorrect, maybe csv file come with extra new lines.
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

                attendee_values = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'first_name2': None,
                    'last_name2': None,
                    'gender': gender_converter.get(Utility.presence(people.get('Sex', '').upper()), GenderEnum.UNSPECIFIED).name,
                    'progressions': {attendee_header: Utility.boolean_or_datetext_or_original(people.get(access_header)) for (access_header, attendee_header) in progression_converter.items() if Utility.presence(people.get(access_header)) is not None},
                    'infos': {
                        'access_people_household_id': household_id,
                        'access_people_values': people,
                    }
                }

                if birth_date:
                    try:
                        attendee_values['actual_birthday'] = datetime.strptime(birth_date, '%m/%d/%Y').date()
                    except ValueError as ve:
                        print("\nImport_attendees error on BirthDate of people: ", people, '. Reason: ', ve, ". This bithday will be skipped. Other columns of this people will still be saved. Continuing. \n")

                if name2:  # assume longest last name is 2 characters
                    break_position = -2 if len(name2) > 2 else -1
                    attendee_values['first_name2'] = name2[break_position:]
                    attendee_values['last_name2'] = name2[:break_position]

                query_values = {
                    'first_name': attendee_values['first_name'],
                    'last_name': attendee_values['last_name'],
                    'first_name2': attendee_values['first_name2'],
                    'last_name2': attendee_values['last_name2'],
                    'infos__access_people_household_id': household_id,
                }

                attendee, attendee_created = Attendee.objects.update_or_create(
                    **{k: v for (k, v) in query_values.items() if v is not None},
                    defaults={k: v for (k, v) in attendee_values.items() if v is not None}
                )

                update_attendee_photo(attendee, Utility.presence(people.get('Photo')))

                if household_role:   # filling temporary family roles
                    family = Family.objects.filter(infos__access_household_id=household_id).first()
                    if family:       # there are some missing records in the access data
                        if household_role == 'A(Self)':
                            relation = Relation.objects.get(title='self')
                            display_order = 0
                            attendee.division = family.division
                        elif household_role == 'B(Spouse)':
                            relation = Relation.objects.get(
                                title__in=['spouse', 'husband', 'wife'],
                                gender=attendee.gender,
                            )  # There are wives mislabelled as 'Male' in Access data
                            display_order = 1
                            attendee.division = family.division
                        else:
                            relation = Relation.objects.get(
                                title__in=['child', 'son', 'daughter'],
                                gender=attendee.gender,
                            )
                            if attendee.age() and attendee.age() < 11:  # k-5
                                attendee.division = division3
                            display_order = 10

                        attendee.save()
                        FamilyAttendee.objects.update_or_create(
                            family=family,
                            attendee=attendee,
                            defaults={'display_order': display_order, 'role': relation}
                        )

                        address_id = family.infos.get('access_household_values', {}).get('AddressID', 'missing')
                        address = Address.objects.filter(fields__access_address_id=address_id).first()
                        if address:
                            AttendeeAddress.objects.update_or_create(
                                address=address,
                                attendee=attendee,
                                defaults={'category': 'from FamilyAddress'}
                            )
                    else:
                        print("\nCannot find the household id: ", household_id, ' for people: ', people, " Other columns of this people will still be saved. Continuing. \n")
            else:
                print('There is no household_id or first/lastname of the people: ', people)
            successfully_processed_count += 1

        except Exception as e:
            print("\nWhile importing/updating people: ", people)
            print('Cannot save import_attendees, reason: ', e)
    print('done!')
    return successfully_processed_count


def reprocess_emails_and_family_roles():
    print("\n\nRunning reprocess_family_roles: \n")
    husband_role = Relation.objects.get(
        title='husband',
        gender=GenderEnum.MALE.name,
    )

    wife_role = Relation.objects.get(
        title='wife',
        gender=GenderEnum.FEMALE.name,
    )

    imported_families = Family.objects.filter(infos__access_household_id__isnull=False).order_by('created')
    successfully_processed_count = 0
    for family in imported_families:
        try:
            print('.', end='')
            children = family.attendees.filter(familyattendee__role__title__in=['child', 'son', 'daughter']).all()
            parents = family.attendees.filter(familyattendee__role__title__in=['self', 'spouse', 'husband', 'wife']).order_by().all()  # order_by() is critical for values_list('gender').distinct() later
            families_address = Address.objects.filter(pk=family.addresses.first().id).first()

            if len(parents) > 1:  # skip for singles
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

                husband = family.attendees.filter(familyattendee__role__title='husband').order_by('created').first()
                wife = family.attendees.filter(familyattendee__role__title='wife').order_by('created').first()

                if families_address:
                    hushand_email = husband.infos.get('access_people_values', {}).get('E-mail')
                    wife_email = wife.infos.get('access_people_values', {}).get('E-mail')
                    families_address.email1 = Utility.presence(hushand_email)
                    families_address.email2 = Utility.presence(wife_email)
                    families_address.save()

                Relationship.objects.update_or_create(
                    from_attendee=wife,
                    to_attendee=husband,
                    relation=husband_role,
                    defaults={
                        'in_family': family,
                        'emergency_contact': husband_role.emergency_contact,
                        'scheduler': husband_role.scheduler,
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
                    }
                )
                successfully_processed_count += 2

            else:
                househead_single = parents.first()
                if househead_single:  # update gender by family role since family role records are better updated.
                    original_household_role = househead_single.infos.get('access_people_values', {}).get('HouseholdRole')
                    if original_household_role == 'B(Spouse)':  # 'Chloris', 'Yvone' are parents > 1
                        househead_single.gender = GenderEnum.FEMALE.name
                        househead_single.save()
                        family_attendee = househead_single.familyattendee_set.first()
                        family_attendee.role = wife_role
                        family_attendee.save()

                if families_address and househead_single:
                    self_email = househead_single.infos.get('access_people_values', {}).get('E-mail')
                    families_address.email1 = Utility.presence(self_email)
                    families_address.save()
                else:
                    print("\nSomehow there's nothing in families_address or househead_single, for family ", family, '. families_address: ', families_address, '. househead_single: ', househead_single, '. household_id: ', family.infos['access_household_id'], '. Continuing to next record.')

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
                                'emergency_contact': househead_role.emergency_contact,
                                'scheduler': househead_role.scheduler,
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
                        }
                    )
                    successfully_processed_count += 2

        except Exception as e:
            print("\nWhile importing/updating relationship for family: ", family)
            print('Cannot save relationship, reason: ', e)
    print('done!')
    return successfully_processed_count


def update_attendee_photo(attendee, photo_names):
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
            attendee.photo.delete()
            attendee.photo.save(picture_name, image_file, True)
            attendee.save()


def check_all_headers():
    #households_headers = ['HouseholdID', 'HousholdLN', 'HousholdFN', 'SpouseFN', 'AddressID', 'HouseholdPhone', 'HouseholdFax', 'AttendenceCount', 'FlyerMailing', 'CardMailing', 'UpdateDir', 'PrintDir', 'LastUpdate', 'HouseholdNote', 'FirstDate', '海沃之友', 'Congregation']
    #peoples_headers = ['LastName', 'FirstName', 'NickName', 'ChineseName', 'Photo', 'Sex', 'Active', 'HouseholdID', 'HouseholdRole', 'E-mail', 'WorkPhone', 'WorkExtension', 'CellPhone', 'BirthDate', 'Skills', 'FirstDate', 'BapDate', 'BapLocation', 'Member', 'MemberDate', 'Fellowship', 'Group', 'LastContacted', 'AssignmentID', 'LastUpdated', 'PeopleNote', 'Christian']
    #addresses_headers = ['AddressID', 'Street', 'City', 'State', 'Zip', 'Country']
    pass


def run(household_csv_file, people_csv_file, address_csv_file, division1_slug, division2_slug, division3_slug, *extras):
    """
    An importer to import old MS Access db data, if same records founds in Attendees db, it will update.
    :param household_csv_file: a comma separated file of household with headers, from MS Access
    :param people_csv_file: a comma separated file of household with headers, from MS Access
    :param address_csv_file: a comma separated file of household with headers, from MS Access
    :param division1_slug: slug of division 1
    :param division2_slug: slug of division 2
    :param division3_slug: slug of division 3
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
    print("Reading extras: ", extras)
    print("Divisions required for importing, running commands: docker-compose -f local.yml run django python manage.py runscript load_access_csv --script-args path/tp/household.csv path/to/people.csv path/to/address.csv division1_slug division2_slug")

    if household_csv_file and people_csv_file and address_csv_file and division1_slug and division2_slug:
        with open(household_csv_file, mode='r', encoding='utf-8-sig') as household_csv, open(people_csv_file, mode='r', encoding='utf-8-sig') as people_csv, open(address_csv_file, mode='r', encoding='utf-8-sig') as address_csv:
            import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug, division3_slug)
