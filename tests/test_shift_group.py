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
    person = Person(
        name="Test", 
        blocked_shifts={}, 
        double_shift=True, 
        max_shifts=5, 
        max_nights=2,
        are_three_shifts_possible=True, 
        night_and_noon_possible=True
    )
    
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
    """Test shift ranking by capacity/need ratios and constraint scores"""
    # Create two people with different shift constraints
    person1 = Person(
        "Person1", 
        blocked_shifts={
            ("Monday", "Morning"): True,
            ("Tuesday", "Morning"): True
        }, 
        double_shift=True, 
        max_shifts=5, 
        max_nights=2,
        are_three_shifts_possible=True, 
        night_and_noon_possible=True
    )
    
    person2 = Person(
        "Person2", 
        blocked_shifts={
            ("Monday", "Morning"): True
        }, 
        double_shift=True, 
        max_shifts=5, 
        max_nights=2,
        are_three_shifts_possible=True, 
        night_and_noon_possible=True
    )
    
    # Add people to the group so get_shift_type_ratios can work
    complete_shift_group.add_person(person1)
    complete_shift_group.add_person(person2)
    
    # Set needed counts for different shift types to create different ratios
    morning_shifts = [
        complete_shift_group.get_shift(day, "Morning") 
        for day in ["Monday", "Tuesday", "Wednesday"]
    ]
    night_shifts = [
        complete_shift_group.get_shift(day, "Night")
        for day in ["Monday", "Tuesday", "Wednesday"]
    ]
    
    # Make morning shifts more constrained than night shifts
    for shift in morning_shifts:
        shift.needed = 2  # Higher need = more constrained
    for shift in night_shifts:
        shift.needed = 1  # Lower need = less constrained
    
    ranked_shifts = complete_shift_group.rank_shifts([person1, person2])
    
    # Debug prints
    print("\nShift type ratios:")
    type_ratios = complete_shift_group.get_shift_type_ratios()
    for shift_type, ratio in type_ratios.items():
        print(f"{shift_type}: {ratio}")
    
    print("\nRanked shifts (first 10):", [f"{s.shift_day} {s.shift_time}" for s in ranked_shifts[:10]])
    
    # Find first morning and night shift in rankings
    first_morning_idx = next(i for i, s in enumerate(ranked_shifts) 
                           if s.shift_time == "Morning" and not s.is_staffed)
    first_night_idx = next(i for i, s in enumerate(ranked_shifts) 
                          if s.shift_time == "Night" and not s.is_staffed)
    
    # Morning shifts should be ranked before night shifts because they have
    # a lower capacity/need ratio (more constrained)
    assert first_morning_idx < first_night_idx, \
        "Shifts with lower capacity/need ratio should be ranked before shifts with higher ratio" 