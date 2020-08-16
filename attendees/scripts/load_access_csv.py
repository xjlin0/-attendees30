import csv, uuid

from attendees.persons.models import Family, FamilyAddress, Utility
from attendees.whereabouts.models import Address, Division


def import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug):
    print("running import_household_people_address ...")
    households = csv.DictReader(household_csv)
    peoples = csv.DictReader(people_csv)
    addresses = csv.DictReader(address_csv)

    try:
        # for household in households:
        #     pass
        #     print(household)
        # for people in peoples:
        #     pass
        #     print(people)
        # for address in addresses:
        #     pass
        #     print(address)
        upserted_address_count = import_addresses(addresses)
        upserted_household_id_count = import_household_ids(households, division1_slug, division2_slug)

        print('Number of address successfully imported/updated: ', upserted_address_count)
        print('Number of households successfully imported/updated: ', upserted_household_id_count)

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
            display_name = (household.get('HousholdFN', '') + ' ' + household.get('SpouseFN', '')).strip()
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
    print("divisions required for importing, running commands: docker-compose -f local.yml run django python manage.py runscript load_access_csv --script-args path/tp/household.csv path/to/people.csv path/to/address.csv cfcc-chinese-ministry cfcc-crossing-ministry")

    if household_csv_file and people_csv_file and address_csv_file and division1_slug and division2_slug:
        with open(household_csv_file, mode='r', encoding='utf-8-sig') as household_csv, open(people_csv_file, mode='r', encoding='utf-8-sig') as people_csv, open(address_csv_file, mode='r', encoding='utf-8-sig') as address_csv:
            import_household_people_address(household_csv, people_csv, address_csv, division1_slug, division2_slug)
