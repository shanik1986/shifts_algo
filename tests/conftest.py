import pytest
from app.google_sheets.import_sheet_data import get_google_sheet_data, get_fresh_data, parse_people_data
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
    Create a fixture for shift a shift group with shift requireements and prople from the Google Sheet.
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
    shift_group = get_fresh_data(
        shift_needs_sheet_name="Test Data - Shift Requirements", 
        people_sheet_name="Test Data - People")
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
    people_sheet_name = "Test Data - People"
    people = parse_people_data(get_google_sheet_data("Shifts", people_sheet_name), sample_shift_group_from_sheet)
    # Get first person dict and convert to Person object
    return people[0]

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
        blocked_shifts={},
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
        blocked_shifts={},
        double_shift=True,
        max_shifts=10,
        max_nights=2,
        are_three_shifts_possible=True,
        night_and_noon_possible=True
    )


@pytest.fixture
def sample_person(complete_shift_group):
    """Creates a fixture Person object with predefined constraints"""
    blocked_shifts = {
        ("Last Saturday", "Night"): True,
        ("Sunday", "Morning"): True,
        ("Monday", "Noon"): True,
        ("Tuesday", "Evening"): True,
        ("Wednesday", "Night"): True,
        ("Thursday", "Morning"): True,
        ("Friday", "Noon"): True,
        ("Saturday", "Evening"): True
    }
    
    return Person(
        name="Random Person 1",
        blocked_shifts=blocked_shifts,
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
        blocked_shifts={}, 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )

    p2 = Person(
        "Bob", 
        blocked_shifts={}, 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p3 = Person(
        "Charlie", 
        blocked_shifts={}, 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p4 = Person(
        "David", 
        blocked_shifts={}, 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    p5 = Person(
        "Ethan", 
        blocked_shifts={}, 
        double_shift=False, 
        max_shifts=10, 
        max_nights=2, 
        are_three_shifts_possible=True,
        night_and_noon_possible=True
        )
    # Set constraint scores
    p1.constraint_scores = {'regular': 1.0, 'night': 1.0, 'weekend': 0.5}
    p2.constraint_scores = {'regular': 1.1, 'night': 2.0, 'weekend': 0.4}
    p3.constraint_scores = {'regular': 2.0, 'night': 3.0, 'weekend': 0.3}
    p4.constraint_scores = {'regular': 3.0, 'night': 5.0, 'weekend': 0.2}
    p5.constraint_scores = {'regular': 6.0, 'night': 6.0, 'weekend': 0.10}
    
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
    Uses names directly from ComboManager.TARGET_PAIRS and ensures non-target names
    are distinct by using 'NOT_TARGET_' prefix.
    """
    default_args = {
        'blocked_shifts': {},
        'double_shift': False,
        'max_shifts': 10,
        'max_nights': 2,
        'are_three_shifts_possible': True,
        'night_and_noon_possible': True
    }
    
    # Create target pair people from ComboManager
    target_pair = next(iter(ComboManager.TARGET_PAIRS))
    first_person = Person(tuple(target_pair)[0], **default_args)
    second_person = Person(tuple(target_pair)[1], **default_args)
    
    # Additional people with names guaranteed not to be in target pairs
    non_target1 = Person("NOT_TARGET_1", **default_args)
    non_target2 = Person("NOT_TARGET_2", **default_args)
    non_target3 = Person("NOT_TARGET_3", **default_args)
    
    # Set same constraint scores initially
    people = [first_person, second_person, non_target1, non_target2, non_target3]
    for p in people:
        p.constraint_scores = {'regular': 1.0, 'night': 1.0, 'weekend': 0.5}
        
    return people

@pytest.fixture
def double_shift_people():
    """Create test people with different double shift capabilities"""
    default_args = {
        'blocked_shifts': {},
        'max_shifts': 10,
        'max_nights': 2,
        'are_three_shifts_possible': True,
        'night_and_noon_possible': True
    }
    
    # Create people with different double shift settings
    double1 = Person("DOUBLE_1", double_shift=True, **default_args)
    double2 = Person("DOUBLE_2", double_shift=True, **default_args)
    no_double1 = Person("NO_DOUBLE_1", double_shift=False, **default_args)
    no_double2 = Person("NO_DOUBLE_2", double_shift=False, **default_args)
    
    # Set same constraint scores initially
    people = [double1, double2, no_double1, no_double2]
    for p in people:
        p.constraint_scores = {'regular': 1.0, 'night': 1.0, 'weekend': 0.5}
        
    return people
