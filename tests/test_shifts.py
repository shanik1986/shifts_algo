import pytest
from app.scheduler.shifts import Shift, VALID_DAYS, VALID_SHIFT_TIMES



def test_shift_creation():
    shift = Shift("Sunday", "Morning")
    assert shift.shift_day == "Sunday"
    assert shift.shift_time == "Morning"

def test_invalid_day():
    with pytest.raises(ValueError, match=r"Invalid day: 'InvalidDay'\. Valid days are: .*Last Saturday.*Sunday.*Monday.*"):
        Shift("InvalidDay", "Morning")

def test_invalid_time():
    with pytest.raises(ValueError, match=r"Invalid shift time: 'afternoon'\. Valid shift times are: .*Morning.*Noon.*Evening.*Night.*"):
        Shift("Monday", "afternoon")

def test_valid_days_and_times():
    # Test that we can create a shift with every valid combination
    for day in VALID_DAYS:
        for time in VALID_SHIFT_TIMES:
            shift = Shift(day, time)
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
def test_is_weekend_shift(day, time, expected):
    shift = Shift(day, time)
    assert shift.is_weekend_shift == expected

def test_adjacent_days():
    # Test middle of week
    wednesday_shift = Shift("Wednesday", "Morning")
    assert wednesday_shift.previous_day == "Tuesday"
    assert wednesday_shift.next_day == "Thursday"
    
    # Test start of week
    last_saturday_shift = Shift("Last Saturday", "Morning")
    assert last_saturday_shift.previous_day is None
    assert last_saturday_shift.next_day == "Sunday"
    
    # Test end of week
    saturday_shift = Shift("Saturday", "Morning")
    assert saturday_shift.previous_day == "Friday"
    assert saturday_shift.next_day is None

def test_adjacent_shifts():
    # Test middle shift
    noon_shift = Shift("Monday", "Noon")
    assert noon_shift.previous_shift == "Morning"
    assert noon_shift.next_shift == "Evening"
    
    # Test first shift
    morning_shift = Shift("Monday", "Morning")
    assert morning_shift.previous_shift is None
    assert morning_shift.next_shift == "Noon"
    
    # Test last shift
    night_shift = Shift("Monday", "Night")
    assert night_shift.previous_shift == "Evening"
    assert night_shift.next_shift is None



def test_shift_comparison():
    # Equal shifts
    shift1 = Shift("Monday", "Morning")
    shift2 = Shift("Monday", "Morning")
    assert shift1 == shift2
    
    # Different shifts
    shift3 = Shift("Monday", "Evening")
    assert shift1 != shift3
    
    # String representation
    assert str(shift1) == "Monday Morning"
    
    # Ordering tests
    monday_morning = Shift("Monday", "Morning")
    monday_noon = Shift("Monday", "Noon")
    monday_evening = Shift("Monday", "Evening")
    monday_night = Shift("Monday", "Night")
    tuesday_morning = Shift("Tuesday", "Morning")
    
    assert monday_morning < monday_noon
    assert monday_noon < monday_evening
    assert monday_evening < monday_night
    assert monday_night < tuesday_morning
    assert not tuesday_morning < monday_morning

def test_shift_collections():
    # Test ALL_SHIFTS contains every combination
    assert len(Shift.ALL_SHIFTS) == len(VALID_DAYS) * len(VALID_SHIFT_TIMES)
    
    # Test that every possible combination exists
    for day in VALID_DAYS:
        for time in VALID_SHIFT_TIMES:
            assert any(s.shift_day == day and s.shift_time == time for s in Shift.ALL_SHIFTS), \
                   f"Missing shift: {day} {time}"
    
    # Test WEEKEND_SHIFTS contains exactly the right shifts
    for shift in Shift.WEEKEND_SHIFTS:
        # Each shift should be either:
        # - A Friday Evening/Night shift
        # - Any Saturday shift
        assert (
            (shift.shift_day == "Friday" and shift.shift_time in ["Evening", "Night"]) or
            (shift.shift_day == "Saturday")
        ), f"Unexpected weekend shift: {shift}"
    
    # Test that all Friday evening/night and Saturday shifts are included
    friday_evening_night = [
        s for s in Shift.ALL_SHIFTS 
        if s.shift_day == "Friday" and s.shift_time in ["Evening", "Night"]
    ]
    saturday_shifts = [
        s for s in Shift.ALL_SHIFTS 
        if s.shift_day == "Saturday"
    ]
    expected_weekend_shifts = friday_evening_night + saturday_shifts
    
    assert len(Shift.WEEKEND_SHIFTS) == len(expected_weekend_shifts), \
           "WEEKEND_SHIFTS missing some expected shifts"
    assert set(Shift.WEEKEND_SHIFTS) == set(expected_weekend_shifts), \
           "WEEKEND_SHIFTS doesn't match expected weekend shifts"


