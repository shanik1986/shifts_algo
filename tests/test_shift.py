import pytest
from app.scheduler.shift import Shift, VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.person import Person
from app.scheduler.shift_group import ShiftGroup


def test_shift_creation(complete_shift_group):
    shift = Shift("Sunday", "Morning", group=complete_shift_group)
    assert shift.shift_day == "Sunday"
    assert shift.shift_time == "Morning"

def test_invalid_day(complete_shift_group):
    with pytest.raises(ValueError, match=r"Invalid day: 'InvalidDay'\. Valid days are: .*Last Saturday.*Sunday.*Monday.*"):
        Shift("InvalidDay", "Morning", group=complete_shift_group)

def test_invalid_time(complete_shift_group):
    with pytest.raises(ValueError, match=r"Invalid shift time: 'afternoon'\. Valid shift times are: .*Morning.*Noon.*Evening.*Night.*"):
        Shift("Monday", "afternoon", group=complete_shift_group)

def test_valid_days_and_times(complete_shift_group):
    # Test that we can create a shift with every valid combination
    for day in VALID_DAYS:
        for time in VALID_SHIFT_TIMES:
            shift = Shift(day, time, group=complete_shift_group)
            assert shift.shift_day == day
            assert shift.shift_time == time

@pytest.mark.parametrize("day,time,expected", [
    # Friday shifts
    ("Friday", "Morning", False),  # Friday morning
    ("Friday", "Noon", False),     # Friday noon
    ("Friday", "Evening", True),   # Friday evening
    ("Friday", "Night", True),     # Friday night
    
    # Saturday shifts
    ("Saturday", "Morning", True),  # Saturday morning
    ("Saturday", "Noon", True),     # Saturday noon
    ("Saturday", "Evening", True),  # Saturday evening
    ("Saturday", "Night", True),    # Saturday night
    
    # Regular weekday
    ("Thursday", "Morning", False),  # Thursday morning
    ("Thursday", "Noon", False),     # Thursday noon
    ("Thursday", "Evening", False),  # Thursday evening
    ("Thursday", "Night", False),    # Thursday night
])
def test_is_weekend_shift(day, time, expected, complete_shift_group):
    shift = Shift(day, time, group=complete_shift_group)
    assert shift.is_weekend_shift == expected

def test_adjacent_days(complete_shift_group):
    # Test middle of week
    wednesday_shift = Shift("Wednesday", "Morning", group=complete_shift_group)
    assert wednesday_shift.previous_day == "Tuesday"
    assert wednesday_shift.next_day == "Thursday"
    
    # Test start of week
    last_saturday_shift = Shift("Last Saturday", "Morning", group=complete_shift_group)
    assert last_saturday_shift.previous_day is None
    assert last_saturday_shift.next_day == "Sunday"
    
    # Test end of week
    saturday_shift = Shift("Saturday", "Morning", group=complete_shift_group)
    assert saturday_shift.previous_day == "Friday"
    assert saturday_shift.next_day is None

def test_adjacent_shifts(complete_shift_group):
    # Test middle shift
    noon_shift = Shift("Monday", "Noon", group=complete_shift_group)
    assert noon_shift.previous_shift == "Morning"
    assert noon_shift.next_shift == "Evening"
    
    # Test first shift
    morning_shift = Shift("Monday", "Morning", group=complete_shift_group)
    assert morning_shift.previous_shift is None
    assert morning_shift.next_shift == "Noon"
    
    # Test last shift
    night_shift = Shift("Monday", "Night", group=complete_shift_group)
    assert night_shift.previous_shift == "Evening"
    assert night_shift.next_shift is None



def test_shift_comparison(complete_shift_group):
    # Equal shifts
    shift1 = Shift("Monday", "Morning", group=complete_shift_group)
    shift2 = Shift("Monday", "Morning", group=complete_shift_group)
    assert shift1 == shift2
    
    # Different shifts
    shift3 = Shift("Monday", "Evening", group=complete_shift_group)
    assert shift1 != shift3
    
    # String representation
    assert str(shift1) == "Monday Morning"
    
    # Ordering tests
    monday_morning = Shift("Monday", "Morning", group=complete_shift_group)
    monday_noon = Shift("Monday", "Noon", group=complete_shift_group)
    monday_evening = Shift("Monday", "Evening", group=complete_shift_group)
    monday_night = Shift("Monday", "Night", group=complete_shift_group)
    tuesday_morning = Shift("Tuesday", "Morning", group=complete_shift_group)
    
    assert monday_morning < monday_noon
    assert monday_noon < monday_evening
    assert monday_evening < monday_night
    assert monday_night < tuesday_morning
    assert not tuesday_morning < monday_morning

def test_shift_collections(complete_shift_group):
    # Test create_all_shifts contains every combination
    all_shifts = Shift.create_all_shifts(complete_shift_group)
    assert len(all_shifts) == len(VALID_DAYS) * len(VALID_SHIFT_TIMES)
    
    # Test that every possible combination exists
    for day in VALID_DAYS:
        for time in VALID_SHIFT_TIMES:
            assert any(s.shift_day == day and s.shift_time == time for s in all_shifts), \
                   f"Missing shift: {day} {time}"
    
    # Test create_weekend_shifts contains exactly the right shifts
    weekend_shifts = Shift.create_weekend_shifts(complete_shift_group)
    for shift in weekend_shifts:
        # Each shift should be either:
        # - A Friday Evening/Night shift
        # - Any Saturday shift
        assert (
            (shift.shift_day == "Friday" and shift.shift_time in ["Evening", "Night"]) or
            (shift.shift_day == "Saturday")
        ), f"Unexpected weekend shift: {shift}"
    
    # Test that all Friday evening/night and Saturday shifts are included
    friday_evening_night = [
        s for s in all_shifts 
        if s.shift_day == "Friday" and s.shift_time in ["Evening", "Night"]
    ]
    saturday_shifts = [
        s for s in all_shifts 
        if s.shift_day == "Saturday"
    ]
    expected_weekend_shifts = friday_evening_night + saturday_shifts
    
    assert len(weekend_shifts) == len(expected_weekend_shifts), \
           "Weekend shifts missing some expected shifts"
    assert set(weekend_shifts) == set(expected_weekend_shifts), \
           "Weekend shifts don't match expected shifts"

def test_shift_needed_attribute(sample_shift_group_from_sheet):
    # Test default value
    shift = Shift("Monday", "Morning", group=sample_shift_group_from_sheet)
    assert shift.needed == 3
    
    # Test custom value
    temp_group = ShiftGroup()
    shift = Shift("Monday", "Morning", needed=2, group=temp_group)
    assert shift.needed == 2
    
    # Test invalid values
    other_temp_group = ShiftGroup()
    with pytest.raises(ValueError, match="must be a non-negative integer"):
        Shift("Monday", "Morning", needed=-1, group=other_temp_group)
    
    with pytest.raises(ValueError, match="must be a non-negative integer"):
        Shift("Monday", "Morning", needed="2", group=other_temp_group)  # type: ignore

def test_shift_string_with_needed(complete_shift_group):
    shift = Shift("Monday", "Morning", needed=2, group=complete_shift_group)
    assert str(shift) == "Monday Morning"  # needed count doesn't affect string representation

def test_shift_assignments(complete_shift_group):
    shift = Shift("Monday", "Morning", needed=2, group=complete_shift_group)
    
    person1 = Person(
        name="Person 1",
        blocked_shifts={},  # No blocked shifts
        double_shift=True,
        max_shifts=5,
        max_nights=2,
        are_three_shifts_possible=True,
        night_and_noon_possible=True,
        max_weekend_shifts=1
    )
    
    person2 = Person(
        name="Person 2",
        blocked_shifts={},
        double_shift=True,
        max_shifts=5,
        max_nights=2,
        are_three_shifts_possible=True,
        night_and_noon_possible=True,
        max_weekend_shifts=1
    )
    
    # Test assignment
    shift.assign_person(person1)
    assert person1 in shift.assigned_people

    
    # Test unassignment
    shift.unassign_person(person1)
    assert person1 not in shift.assigned_people



