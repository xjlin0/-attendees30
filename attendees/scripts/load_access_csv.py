import csv
from collections import namedtuple


def import_household_people_address(household_csv, people_csv, address_csv):
    print("running import_household_people_address ...")
    pass


def run(household_csv_file, people_csv_file, address_csv_file, *extras):
    """
    An importer to import old MS Access db data, if same records founds in Attendees db, it will update.
    :param household_csv_file: a comma separated file of household with headers, from MS Access
    :param people_csv_file: a comma separated file of household with headers, from MS Access
    :param address_csv_file: a comma separated file of household with headers, from MS Access
    :param extras: other arguments
    :return: None, but write to Attendees db (create or update)
    """

    print("running load_access_csv.py... with arguments: ")
    print("here is household_csv_file: ", household_csv_file)
    print("here is people_csv_file: ", people_csv_file)
    print("here is address_csv_file: ", address_csv_file)
    print(extras)

    if household_csv_file and people_csv_file and address_csv_file:
        with open(household_csv_file) as household_csv, open(people_csv_file) as people_csv, open(address_csv_file) as address_csv:
            import_household_people_address(household_csv, people_csv, address_csv)
