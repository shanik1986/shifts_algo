import pytest
from app.google_sheets.import_sheet_data import get_google_sheet_data, parse_shift_constraints, parse_shift_requirements
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

#Create a fixture for empty current assignments
@pytest.fixture
def sample_current_assignments():
    """Create a fixture for current assignments"""
    return {day: {shift: [] for shift in SHIFTS} for day in DAYS}

#Create a fixture for a sample shift constraints
@pytest.fixture
def sample_shift_constraints():
    """
    Create a fixture for shift requirements from the Google Sheet.
    The requirements are:
        Last Saturday Night: 0
        All shifts on Sunday and Monday: 3
        Tuesday Morning: 2
        Tuesday Noon: 4
        Tuesday Evening: 5
        Tuesday Night: 2
        All shifts on Wednesday, Thursday, Friday, Saturday except for Wednesday Evening: 1
        Wednesday Evening: 0
        Saturday Morning, Noon, Evening: 3
        Saturday Night: 0
    """
    shift_requirements_data = get_google_sheet_data("Shifts", "Test Data - Shift Requirements")
    processed_data = parse_shift_requirements(shift_requirements_data)
    return processed_data

#Create a fixture of a person who won't the different types of shifts
@pytest.fixture
def sample_person_with_constraints():
    """
    This person will have the following constraints:
        double_shift: False
        are_three_shifts_possible: False
        night_and_noon_possible: False
    """
    return Person(
        name="Constrainned Person",
        unavailable=[],
        double_shift=False,
        max_shifts=10,
        max_nights=1,
        are_three_shifts_possible=False,
        night_and_noon_possible=False
    )

#Create a fixture of a person with no constraints
@pytest.fixture
def sample_person_with_no_constraints():
    """
    This person will have the following constraints:
        double_shift: True
        are_three_shifts_possible: True
        night_and_noon_possible: True
    """
    return Person(
        name="No Constraints Person",
        unavailable=[],
        double_shift=True,
        max_shifts=10,
        max_nights=2,
        are_three_shifts_possible=True,
        night_and_noon_possible=True
    )
