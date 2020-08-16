import csv
from datetime import datetime
from attendees.persons.models import Family, FamilyAddress, Utility, GenderEnum, Attendee
from attendees.whereabouts.models import Address, Division


def import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug):
    print("running import_household_people_address ...")
    households = csv.DictReader(household_csv)
    peoples = csv.DictReader(people_csv)
    addresses = csv.DictReader(address_csv)

    try:
        upserted_address_count = import_addresses(addresses)
        upserted_household_id_count = import_household_ids(households, division1_slug, division2_slug)
        upserted_attendee_count = import_attendee_id(peoples)
        print('Number of address successfully imported/updated: ', upserted_address_count)
        print('Number of households successfully imported/updated: ', upserted_household_id_count)
        print('Number of people successfully imported/updated: ', upserted_attendee_count)
    except Exception as e:
        print('Cannot proceed import_household_people_address, reason: ', e)

    pass


def import_addresses(addresses):
    try:
        count = 0
        for address in addresses:
            print('Importing/updating: ', address)
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
                count += 1
        return count

    except Exception as e:
        print('Cannot proceed import_addresses, reason: ', e)
    pass


def import_household_ids(households, division1_slug, division2_slug):
    division1 = Division.objects.get(slug=division1_slug)
    division2 = Division.objects.get(slug=division2_slug)
    division_converter = {
        'CH': division1,
        'EN': division2,
    }
    try:
        count = 0
        for household in households:
            print('Importing/updating: ', household)
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

                count += 1
        return count

    except Exception as e:
        print('Cannot proceed import_households, reason: ', e)
    pass


def import_attendee_id(peoples):
    gender_converter = {
        'F': GenderEnum.FEMALE,
        'M': GenderEnum.MALE,
    }
    try:
        count = 0
        for people in peoples:
            print('Importing/updating: ', people)
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
                    'infos': {
                        'access_people_household_id': household_id,
                        'access_people_values': people,
                    }
                }

                if birth_date:
                    try:
                        attendee_values['actual_birthday'] = datetime.strptime(birth_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                    except ValueError:
                        print('import_attendee_id error on BirthDate, people: ', people)

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

                Attendee.objects.update_or_create(
                    **{k: v for (k, v) in query_values.items() if v is not None},
                    defaults={k: v for (k, v) in attendee_values.items() if v is not None}
                )
                count += 1
        return count

    except Exception as e:
        print('Cannot proceed import_addresses, reason: ', e)
    pass

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

    print("running load_access_csv.py... with arguments: ")
    print("here is household_csv_file: ", household_csv_file)
    print("here is people_csv_file: ", people_csv_file)
    print("here is address_csv_file: ", address_csv_file)
    print(division1_slug)
    print(division2_slug)
    print(extras)
    print("divisions required for importing, running commands: docker-compose -f local.yml run django python manage.py runscript load_access_csv --script-args path/tp/household.csv path/to/people.csv path/to/address.csv division1_slug division2_slug")

    if household_csv_file and people_csv_file and address_csv_file and division1_slug and division2_slug:
        with open(household_csv_file, mode='r', encoding='utf-8-sig') as household_csv, open(people_csv_file, mode='r', encoding='utf-8-sig') as people_csv, open(address_csv_file, mode='r', encoding='utf-8-sig') as address_csv:
            import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug)
