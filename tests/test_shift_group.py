import pytest
from app.scheduler.shift_group import ShiftGroup
from app.scheduler.shift import Shift
from app.scheduler.person import Person

def test_shift_management(complete_shift_group):
    """Test basic shift management functions"""
    # Test add_shift
    group = ShiftGroup()
    shift = Shift("Monday", "Morning", group=group)
    group.add_shift(shift)
    assert shift in group.shifts
    
    # Test get_shift
    assert group.get_shift("Monday", "Morning") == shift
    assert group.get_shift("Invalid", "Time") is None
    
    # Test get_all_same_day_shifts
    monday_shifts = group.get_all_shifts_from_day("Monday")
    assert len(monday_shifts) == 1
    assert monday_shifts[0] == shift

def test_group_constraints(complete_shift_group):
    """Test group-level constraint checking"""
    person = Person("Test", [], double_shift=True, max_shifts=5, max_nights=2,
                   are_three_shifts_possible=True, night_and_noon_possible=True)
    
    # Test morning after night
    night_shift = complete_shift_group.get_shift("Monday", "Night")
    morning_shift = complete_shift_group.get_shift("Tuesday", "Morning")
    person.assign_to_shift(night_shift)
    assert complete_shift_group.is_morning_after_night(person, morning_shift)
    
    # Test consecutive shifts
    noon_shift = complete_shift_group.get_shift("Monday", "Noon")
    evening_shift = complete_shift_group.get_shift("Monday", "Evening")
    person.assign_to_shift(noon_shift)
    assert complete_shift_group.is_consecutive_shift(person, evening_shift)
    
    # Test third shift
    person.assign_to_shift(evening_shift)
    night_shift = complete_shift_group.get_shift("Monday", "Night")
    assert complete_shift_group.is_third_shift(person, night_shift)

def test_rank_shifts(complete_shift_group):
    """Test shift ranking by constraint level"""
    person1 = Person("Person1", [], double_shift=True, max_shifts=5, max_nights=2,
                    are_three_shifts_possible=True, night_and_noon_possible=True)
    person2 = Person("Person2", [], double_shift=True, max_shifts=5, max_nights=2,
                    are_three_shifts_possible=True, night_and_noon_possible=True)
    
    # Make one shift more constrained
    person1.unavailable = [complete_shift_group.get_shift("Monday", "Morning")]
    
    ranked_shifts = complete_shift_group.rank_shifts([person1, person2])
    
    # Most constrained shift should be first
    assert ranked_shifts[0].shift_day == "Monday"
    assert ranked_shifts[0].shift_time == "Morning" 