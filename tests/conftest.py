import pytest
from app.google_sheets.import_sheet_data import get_google_sheet_data, parse_shift_constraints
from app.scheduler.person import Person
from app.scheduler.constants import DAYS, SHIFTS

@pytest.fixture
def sample_person_dict_from_sheet():
    """
    Creates as a fixture a dictionary from the first row of data in the Google Sheet
    Test shift blocking functionality
    Blocked shifts: 
        Last Saturday Night,
        Sunday Morning,
        Monday Noon,
        Tuesday Evening,
        Wednesday Night,
        Thursday Morning,
        Friday Noon,
        Saturday Evening
    All the rest of the shifts are available
    """
    shift_constraint_data = get_google_sheet_data("Shifts", "Test Data - People")
    processed_data = parse_shift_constraints(shift_constraint_data)
    # Get first person dict and convert to Person object
    return processed_data[0]

@pytest.fixture
def sample_person_from_sheet():
    """Creates as a fixture a Person object from the first row of data in the Google Sheet
    Test shift blocking functionality
    Blocked shifts: 
        Last Saturday Night,
        Sunday Morning,
        Monday Noon,
        Tuesday Evening,
        Wednesday Night,
        Thursday Morning,
        Friday Noon,
        Saturday Evening
    All the rest of the shifts are available
    """
    shift_constraint_data = get_google_sheet_data("Shifts", "Test Data - People")
    processed_data = parse_shift_constraints(shift_constraint_data)
    # Get first person dict and convert to Person object
    return Person.from_dict(processed_data[0])


