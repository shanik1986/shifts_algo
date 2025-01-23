import pytest
from app.google_sheets.import_sheet_data import get_google_sheet_data, parse_shift_constraints, create_shift_group_from_requirements
from app.scheduler.person import Person
from app.scheduler.shift import VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.shift_group import ShiftGroup
from app.scheduler.shift import Shift
from app.scheduler.combo_manager import ComboManager
from itertools import combinations
#Create a fixture for a sample shift constraints
@pytest.fixture
def sample_shift_group_from_sheet():
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
    shift_group = create_shift_group_from_requirements(shift_requirements_data)
    return shift_group

@pytest.fixture
def complete_shift_group():
    """Creates a ShiftGroup containing all possible shifts"""
    group = ShiftGroup()
    for day in VALID_DAYS:
        for time in VALID_SHIFT_TIMES:
            shift = Shift(day, time, needed = 3, group=group)
            group.add_shift(shift)
    return group


@pytest.fixture
def sample_person_from_sheet(sample_shift_group_from_sheet):
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
    processed_data = parse_shift_constraints(shift_constraint_data, sample_shift_group_from_sheet)
    # Get first person dict and convert to Person object
    return processed_data[0]

#Create a fixture for empty current assignments
@pytest.fixture
def sample_current_assignments():
    """Create a fixture for current assignments"""
    return []


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


@pytest.fixture
def sample_person(complete_shift_group):
    """Creates a fixture Person object with predefined constraints"""
    unavailable_shifts = [
        shift for shift in complete_shift_group.shifts 
        if (shift.shift_day, shift.shift_time) in [
            ("Last Saturday", "Night"),
            ("Sunday", "Morning"),
            ("Monday", "Noon"),
            ("Tuesday", "Evening"),
            ("Wednesday", "Night"),
            ("Thursday", "Morning"),
            ("Friday", "Noon"),
            ("Saturday", "Evening")
        ]
    ]
    
    return Person(
        name="Random Person 1",
        unavailable=unavailable_shifts,
        double_shift=False,
        max_shifts=5,
        max_nights=2,
        are_three_shifts_possible=False,
        night_and_noon_possible=True,
        shift_counts=0,
        night_counts=0
    )

@pytest.fixture
def sample_people():
    # Create test people with different constraint scores
    p1 = Person(
        "Alice", 
        unavailable=[], 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )

    p2 = Person(
        "Bob", 
        unavailable=[], 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p3 = Person(
        "Charlie", 
        unavailable=[], 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p4 = Person(
        "David", 
        unavailable=[], 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p5 = Person(
        "Ethan", 
        unavailable=[], 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    # Set constraint scores
    p1.constraints_score = 1.0
    p2.constraints_score = 1.1
    p3.constraints_score = 2.0
    p4.constraints_score = 3.0
    p5.constraints_score = 6.0
    
    return [p1, p2, p3, p4, p5]

@pytest.fixture
def sample_combination_list_from_people(sample_people):
    """
    Output:
    [
        [p1, p2],
        [p1, p3],
        [p1, p4],
        [p1, p5],
        [p2, p3],
        [p2, p4],
        [p2, p5],
        [p3, p4],
        [p3, p5],
        [p4, p5]
    ]
    """
    # Create a list of combinations from the sample people
    return [list(combo) for combo in combinations(sample_people, 2)]

@pytest.fixture
def combo_manager():
    return ComboManager()

@pytest.fixture
def target_names_people_with_same_constraint_score():
    """Create test people with specific names for target pairs testing.
    Matches the structure in ComboManager.target_names:
    [
        {"Avishay", "Shani Keynan"},
        {"Shani Keynan", "Eliran Ron"},
        {"Shani Keynan", "Nir Ozery"},
        {"Shani Keynan", "Yoram"},
        {"Shani Keynan", "Maor"}
    ]
    """
    # Create test people with exact names from ComboManager's target_names
    default_args = {
        'unavailable': [],
        'double_shift': False,
        'max_shifts': 10,
        'max_nights': 2,
        'are_three_shifts_possible': True,
        'night_and_noon_possible': True
    }
    
    avishay = Person("Avishay", **default_args)
    shani = Person("Shani Keynan", **default_args)
    eliran = Person("Eliran Ron", **default_args)
    nir = Person("Nir Ozery", **default_args)
    yoram = Person("Yoram", **default_args)
    maor = Person("Maor", **default_args)
    other = Person("Other Person", **default_args)
    
    # Set same constraint scores initially
    for p in [avishay, shani, eliran, nir, yoram, maor, other]:
        p.constraints_score = 1.0
        
    # Return both the people dict and the target pairs structure
    return {
        'people': {
            'avishay': avishay,
            'shani': shani,
            'eliran': eliran,
            'nir': nir,
            'yoram': yoram,
            'maor': maor,
            'other': other
        },
        'target_pairs': [
            {avishay.name, shani.name},
            {shani.name, eliran.name},
            {shani.name, nir.name},
            {shani.name, yoram.name},
            {shani.name, maor.name}
        ]
    }
