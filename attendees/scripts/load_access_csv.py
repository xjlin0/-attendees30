import csv
from datetime import datetime
from itertools import permutations

from django.db.models.aggregates import Count

from attendees.persons.models import Utility, GenderEnum, Family, FamilyAddress, Relation, Attendee, FamilyAttendee, AttendeeAddress, Relationship
from attendees.whereabouts.models import Address, Division


def import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug):
    print("\n\n\nStarting import_household_people_address ...\n\n")
    households = csv.DictReader(household_csv)
    peoples = csv.DictReader(people_csv)
    addresses = csv.DictReader(address_csv)

    try:
        upserted_address_count = import_addresses(addresses)
        upserted_household_id_count = import_household_ids(households, division1_slug, division2_slug)
        upserted_attendee_count = import_attendee_id(peoples)
        print("\n\nProcessing results of importing/updating Access export csv files:\n")
        print('Number of address successfully imported/updated: ', upserted_address_count)
        print('Number of households successfully imported/updated: ', upserted_household_id_count)
        print('Number of people successfully imported/updated: ', upserted_attendee_count)

        if upserted_address_count and upserted_household_id_count and upserted_attendee_count:
            upserted_relationship_count = reprocess_family_roles()
            print("\nNumber of relationship successfully imported/updated: ", upserted_relationship_count)
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
    return successfully_processed_count


def import_household_ids(households, division1_slug, division2_slug):
    division1 = Division.objects.get(slug=division1_slug)
    division2 = Division.objects.get(slug=division2_slug)
    division_converter = {
        'CH': division1,
        'EN': division2,
    }
    print("\n\nRunning import_household_ids:\n")
    successfully_processed_count = 0  # households.line_num always advances despite of processing success
    for household in households:
        try:
            print('.', end='')
            household_id = Utility.presence(household.get('HouseholdID'))
            address_id = Utility.presence(household.get('AddressID'))
            display_name = (household.get('HousholdLN', '') + ' ' + household.get('HousholdFN', '') + ' ' + household.get('SpouseFN', '')).strip()
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
    return successfully_processed_count


def import_attendee_id(peoples):
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
    print("\n\nRunning import_attendee_id: \n")
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
                        attendee_values['actual_birthday'] = datetime.strptime(birth_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                    except ValueError as ve:
                        print("\nImport_attendee_id error on BirthDate of people: ", people, '. Reason: ', ve, ". This bithday will be skipped. Other columns of this people will still be saved. Continuing \n")

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

                if household_role:   # filling temporary family roles
                    family = Family.objects.filter(infos__access_household_id=household_id).first()
                    if family:       # there are some missing records in the access data
                        if household_role == 'A(Self)':
                            relation = Relation.objects.get(title='self')
                            display_order = 0
                        elif household_role == 'B(Spouse)':
                            relation = Relation.objects.get(title='spouse')
                            display_order = 1
                        else:
                            relation = Relation.objects.get(title='child')
                            display_order = 10

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
                        print("\nCannot find the household id: ", household_id, ' for people: ', people, " Other columns of this people will still be saved. Continuing \n")
            successfully_processed_count += 1

        except Exception as e:
            print("\nWhile importing/updating people: ", people)
            print('Cannot save import_attendee_id, reason: ', e)
    return successfully_processed_count


def reprocess_family_roles():
    print("\n\nRunning reprocess_family_roles: \n")
    imported_non_single_families = Family.objects.annotate(
                                            attendee_count=Count('familyattendee'),
                                        ).filter(
                                            attendee_count__gt=1,
                                            infos__access_household_id__isnull=False
                                        ).order_by('created')
    successfully_processed_count = 0
    for family in imported_non_single_families:
        try:
            print('.', end='')
            children = family.attendees.filter(familyattendee__role__title='child').all()
            siblings = permutations(children, 2)
            for (from_child, to_child) in siblings:
                relation = Relation.objects.filter(
                    title__in=['brother', 'sister', 'sibling'],
                    gender=to_child.gender,
                ).first()
                if relation:
                    Relationship.objects.update_or_create(
                        from_attendee=from_child,
                        to_attendee=to_child,
                        relation=relation,
                        defaults={
                                    'in_family': family,
                                    'emergency_contact': relation.emergency_contact,
                                    'scheduler': relation.scheduler,
                                 }
                    )
                    successfully_processed_count += 1
        except Exception as e:
            print("\nWhile importing/updating relationship for family: ", family)
            print('Cannot save relationship, reason: ', e)
    return successfully_processed_count


def check_all_headers():
    #households_headers = ['HouseholdID', 'HousholdLN', 'HousholdFN', 'SpouseFN', 'AddressID', 'HouseholdPhone', 'HouseholdFax', 'AttendenceCount', 'FlyerMailing', 'CardMailing', 'UpdateDir', 'PrintDir', 'LastUpdate', 'HouseholdNote', 'FirstDate', '海沃之友', 'Congregation']
    #peoples_headers = ['LastName', 'FirstName', 'NickName', 'ChineseName', 'Photo', 'Sex', 'Active', 'HouseholdID', 'HouseholdRole', 'E-mail', 'WorkPhone', 'WorkExtension', 'CellPhone', 'BirthDate', 'Skills', 'FirstDate', 'BapDate', 'BapLocation', 'Member', 'MemberDate', 'Fellowship', 'Group', 'LastContacted', 'AssignmentID', 'LastUpdated', 'PeopleNote', 'Christian']
    #addresses_headers = ['AddressID', 'Street', 'City', 'State', 'Zip', 'Country']
    pass


def run(household_csv_file, people_csv_file, address_csv_file, division1_slug, division2_slug, *extras):
    """
    An importer to import old MS Access db data, if same records founds in Attendees db, it will update.
    :param household_csv_file: a comma separated file of household with headers, from MS Access
    :param people_csv_file: a comma separated file of household with headers, from MS Access
    :param address_csv_file: a comma separated file of household with headers, from MS Access
    :param division1_slug: slug of division 1
    :param division1_slug: slug of division 2
    :param extras: optional other arguments
    :return: None, but write to Attendees db (create or update)
    """

    print("Running load_access_csv.py... with arguments: ")
    print("Reading household_csv_file: ", household_csv_file)
    print("Reading people_csv_file: ", people_csv_file)
    print("Reading address_csv_file: ", address_csv_file)
    print("Reading division1_slug: ", division1_slug)
    print("Reading division2_slug: ", division2_slug)
    print("Reading extras: ", extras)
    print("Divisions required for importing, running commands: docker-compose -f local.yml run django python manage.py runscript load_access_csv --script-args path/tp/household.csv path/to/people.csv path/to/address.csv division1_slug division2_slug")

    if household_csv_file and people_csv_file and address_csv_file and division1_slug and division2_slug:
        with open(household_csv_file, mode='r', encoding='utf-8-sig') as household_csv, open(people_csv_file, mode='r', encoding='utf-8-sig') as people_csv, open(address_csv_file, mode='r', encoding='utf-8-sig') as address_csv:
            import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug)
