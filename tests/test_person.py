import pytest
from app.scheduler.person import Person
from app.scheduler.shift import Shift, VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.shift_group import ShiftGroup


def test_shift_blocking(sample_person):
    """Test shift blocking using Shift objects"""
    temp_group = ShiftGroup()
    assert sample_person.is_shift_blocked(
        Shift("Last Saturday", "Night", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Sunday", "Morning", group=temp_group)) == True
    
    # Test available shifts
    assert sample_person.is_shift_blocked(Shift("Sunday", "Noon", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Monday", "Morning", group=temp_group)) == False

def test_shift_assignment_and_unassignment(sample_person, complete_shift_group):
    shift = Shift("Sunday", "Noon", group=complete_shift_group)
    
    # Assign person to a shift
    sample_person.assign_to_shift(shift)
    assert sample_person in shift.assigned_people
    assert sample_person.shift_counts == 1
    assert sample_person.night_counts == 0

    # Unassign person from a shift
    sample_person.unassign_from_shift(shift)
    assert sample_person not in shift.assigned_people
    assert sample_person.shift_counts == 0
    assert sample_person.night_counts == 0

def test_night_assignment_and_unassignment(sample_person, complete_shift_group):
    night_shift = Shift("Sunday", "Night", group=complete_shift_group)
    
    # Assign person to a night shift
    sample_person.assign_to_shift(night_shift)
    assert sample_person in night_shift.assigned_people
    assert sample_person.shift_counts == 1
    assert sample_person.night_counts == 1

    # Unassign person from a night shift
    sample_person.unassign_from_shift(night_shift)
    assert sample_person not in night_shift.assigned_people
    assert sample_person.shift_counts == 0
    assert sample_person.night_counts == 0

def test_max_shifts_constraint(sample_person, complete_shift_group):
    """Test max shifts constraint"""
    shift = Shift("Sunday", "Noon", group=complete_shift_group)
    # Assign up to max shifts
    for i in range(sample_person.max_shifts):
        assert sample_person.is_max_shifts_reached() == False
        sample_person.assign_to_shift(shift)
    
    assert sample_person.is_max_shifts_reached() == True
    sample_person.unassign_from_shift(shift)
    assert sample_person.is_max_shifts_reached() == False

def test_max_nights_constraint(sample_person, complete_shift_group):
    """Test max nights constraint"""
    night_shift = Shift("Sunday", "Night", group=complete_shift_group) 
    other_night_shift = Shift("Monday", "Night", group=complete_shift_group)
    last_night_shift = Shift("Tuesday", "Night", group=complete_shift_group)
    shifts_to_assign = [night_shift, other_night_shift]

    # Assign up to max nights
    for shift in shifts_to_assign:
        print(f"\nBefore assigning {shift}:")
        print(f"night_counts: {sample_person.night_counts}")
        print(f"max_nights_reached: {sample_person.is_max_nights_reached()}")
        assert sample_person.is_max_nights_reached() == False
        sample_person.assign_to_shift(shift)
        print(f"After assigning {shift}:")
        print(f"night_counts: {sample_person.night_counts}")
        
    print("\nAfter assigning both shifts:")
    print(f"night_counts: {sample_person.night_counts}")
    print(f"max_nights_reached: {sample_person.is_max_nights_reached()}")
    assert sample_person.is_max_nights_reached() == True
    assert sample_person.is_eligible_for_shift(last_night_shift) == False

    print("\nBefore unassigning shift:")
    print(f"night_counts: {sample_person.night_counts}")
    sample_person.unassign_from_shift(night_shift)
    print("\nAfter unassigning shift:")
    print(f"night_counts: {sample_person.night_counts}")
    print(f"max_nights_reached: {sample_person.is_max_nights_reached()}")
    assert sample_person.is_max_nights_reached() == False

    print("\nChecking eligibility for last night shift:")
    print(f"night_counts: {sample_person.night_counts}")
    print(f"is_eligible: {sample_person.is_eligible_for_shift(last_night_shift)}")
    assert sample_person.is_eligible_for_shift(last_night_shift) == True

def test_weekend_shift_limitation(sample_person, complete_shift_group):
    person = Person(
        name="Test Person",
        unavailable=[],
        double_shift=True,
        max_shifts=10,
        max_nights=5,
        are_three_shifts_possible=True,
        night_and_noon_possible=True
    )
    
    # First weekend shift should be allowed
    assert person.is_eligible_for_shift(Shift("Friday", "Evening", group=complete_shift_group)) == True
    person.assign_to_shift(Shift("Friday", "Evening", group=complete_shift_group))
    
    # Second weekend shift should not be allowed
    assert person.is_eligible_for_shift(Shift("Saturday", "Morning", group=complete_shift_group)) == False
    
    # Unassigning should make weekend shifts available again
    person.unassign_from_shift(Shift("Friday", "Evening", group=complete_shift_group))
    assert person.is_eligible_for_shift(Shift("Saturday", "Morning", group=complete_shift_group)) == True

def test_shift_counts(sample_person, complete_shift_group):
    """Test shift counting (regular, night, weekend)"""
    # Regular shift
    day_shift = Shift("Monday", "Morning", group=complete_shift_group)
    sample_person.assign_to_shift(day_shift)
    assert sample_person.shift_counts == 1
    assert sample_person.night_counts == 0
    assert sample_person.weekend_shifts == 0
    
    # Night shift
    night_shift = Shift("Tuesday", "Night", group=complete_shift_group)
    sample_person.assign_to_shift(night_shift)
    assert sample_person.shift_counts == 2
    assert sample_person.night_counts == 1
    
    # Weekend shift
    weekend_shift = Shift("Saturday", "Morning", group=complete_shift_group)
    sample_person.assign_to_shift(weekend_shift)
    assert sample_person.shift_counts == 3
    assert sample_person.weekend_shifts == 1
    
    # Unassign and verify counts decrease
    sample_person.unassign_from_shift(night_shift)
    assert sample_person.shift_counts == 2
    assert sample_person.night_counts == 0

def test_max_limits(sample_person, complete_shift_group):
    """Test maximum shift/night limits"""
    shift = Shift("Monday", "Morning", group=complete_shift_group)
    night_shift = Shift("Monday", "Night", group=complete_shift_group)
    
    # Test max shifts
    for _ in range(sample_person.max_shifts):
        assert not sample_person.is_max_shifts_reached()
        sample_person.assign_to_shift(shift)
    assert sample_person.is_max_shifts_reached()
    
    # Reset
    sample_person.unassign_from_shift(shift)
    
    # Test max nights
    for _ in range(sample_person.max_nights):
        assert not sample_person.is_max_nights_reached()
        sample_person.assign_to_shift(night_shift)
    assert sample_person.is_max_nights_reached()

def test_calculate_constraint_score(sample_person):
    """
    Test constraint score calculation
    Sample person relevant attributes:
        Max shifts: 5
        Max nights: 2
        Night + Noon possible: True
        Double shift: False

        Unavailable: [
            ("Saturday", "Night"), 
            ("Sunday", "Morning"), 
            ("Monday", "Noon"), 
            ("Tuesday", "Evening"), 
            ("Wednesday", "Night"),
            ("Thursday", "Morning"),
            ("Friday", "Noon"),
            ("Saturday", "Evening")
        ]
    """
    group = ShiftGroup()
    group.add_shift(Shift("Sunday", "Morning", group=group, needed=1))
    group.add_shift(Shift("Sunday", "Noon", group=group, needed=1))
    group.add_shift(Shift("Sunday", "Evening", group=group, needed=1))
    group.add_shift(Shift("Monday", "Morning", group=group, needed=1))
    group.add_shift(Shift("Monday", "Evening", group=group, needed=1))
    
    #Assign to Sunday Night
    sample_person.assign_to_shift(Shift("Sunday", "Night", group=group, needed=1))
    

    # Calculate initial constraint score
    assert sample_person.calculate_constraint_score(group) == 0.5
    
    # Assign to Monday evening to reduce constraint score
    sample_person.assign_to_shift(Shift("Monday", "Evening", group=group))
    
    # Calculate new constraint score
    assert sample_person.calculate_constraint_score(group) == (1/3)
    
    # Assign to Thursday morning, Saturday morning and Saturday night to make the person completely unavailable
    sample_person.assign_to_shift(Shift("Saturday", "Morning", group=group))
    assert sample_person.calculate_constraint_score(group) == (1/2)
    
    sample_person.assign_to_shift(Shift("Saturday", "Night", group=group))
    assert sample_person.calculate_constraint_score(group) == (1)
    
    sample_person.assign_to_shift(Shift("Thursday", "Morning", group=group))
    assert sample_person.calculate_constraint_score(group) == float("inf")
   