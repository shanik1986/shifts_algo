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

    # Increase max weekend shifts to 2 and assert that the second weekend shift is now allowed
    person.max_weekend_shifts = 2
    assert person.is_eligible_for_shift(Shift("Saturday", "Morning", group=complete_shift_group)) == True
    person.assign_to_shift(Shift("Saturday", "Morning", group=complete_shift_group))
    assert person.is_eligible_for_shift(Shift("Saturday", "Evening", group=complete_shift_group)) == False
    
    # Unassigning should make weekend shifts available again
    person.unassign_from_shift(Shift("Friday", "Evening", group=complete_shift_group))
    assert person.is_eligible_for_shift(Shift("Saturday", "Evening", group=complete_shift_group)) == True

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
        Max weekend shifts: 1
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
    
    # Add regular shifts - 3 total needed regular shifts 
    group.add_shift(Shift("Monday", "Morning", needed=1, group=group))
    group.add_shift(Shift("Tuesday", "Morning", needed=1, group=group))
    group.add_shift(Shift("Sunday", "Morning", needed=1, group=group))
    
    # Add night shifts  - 4 total needed night shifts
    group.add_shift(Shift("Monday", "Night", needed=1, group=group))
    group.add_shift(Shift("Tuesday", "Night", needed=1, group=group))
    group.add_shift(Shift("Wednesday", "Night", needed=1, group=group))
    group.add_shift(Shift("Sunday", "Night", needed=1, group=group))
    
    # Add weekend shifts - 2 total needed weekend shifts
    group.add_shift(Shift("Saturday", "Morning", needed=1, group=group))
    group.add_shift(Shift("Friday", "Evening", needed=1, group=group))

    # Initial state:
    scores = sample_person.calculate_constraint_score(group)
    assert scores['regular'] == 2/3  # 2 eligible regular shifts / 3 remaining regular shifts (5 max shifts minus 2 night shifts == 3)
    assert scores['night'] == 3/2    # 3 eligible night shifts / 2 remaining night shift capacity
    assert scores['weekend'] == 2/1   # 2 eligible weekend shift / 1 remaining weekend shift capacity

    # Test error handling by mocking calculate_constraint_score to return invalid scores
    def mock_calculate_scores_missing(self):
        return {'night': 0.5, 'weekend': 0.5}  # Missing 'regular'
    
    original_method = Person.calculate_constraint_score
    Person.calculate_constraint_score = mock_calculate_scores_missing
    with pytest.raises(ValueError, match=f"Missing constraint scores {{'regular'}} for person {sample_person.name}"):
        sample_person._validate_constraint_scores(mock_calculate_scores_missing(sample_person))
    
    def mock_calculate_scores_invalid(self):
        return {
            'regular': 0.5,
            'night': 0.5,
            'weekend': 0.5,
            'invalid_type': 0.5
        }
    
    Person.calculate_constraint_score = mock_calculate_scores_invalid
    with pytest.raises(ValueError, match=f"Invalid constraint score keys for person {sample_person.name}"):
        sample_person._validate_constraint_scores(mock_calculate_scores_invalid(sample_person))
    
    # Restore original method
    Person.calculate_constraint_score = original_method

    # Reset constraint scores for remaining tests
    sample_person.constraint_scores = {}
    scores = sample_person.calculate_constraint_score(group)

    # Assign a regular shift
    sample_person.assign_to_shift(Shift("Monday", "Morning", group=group))
    scores = sample_person.calculate_constraint_score(group)
    assert scores['regular'] == 1/2  # 1 eligible regular shift / 2 remaining shifts

    # Assign a night shift
    sample_person.assign_to_shift(Shift("Monday", "Night", group=group))
    scores = sample_person.calculate_constraint_score(group)
    assert scores['night'] == 1/1    # 1 eligible night shift / 1 remaining night

    # Assign a weekend shift
    sample_person.assign_to_shift(Shift("Friday", "Evening", group=group))
    scores = sample_person.calculate_constraint_score(group)
    assert scores['weekend'] == float('inf')  # No more weekend capacity

    # Fill up night shifts
    sample_person.assign_to_shift(Shift("Tuesday", "Night", group=group))
    scores = sample_person.calculate_constraint_score(group)
    assert scores['night'] == float('inf')  # No more night capacity

    # Fill up regular shifts
    sample_person.assign_to_shift(Shift("Tuesday", "Morning", group=group))
    scores = sample_person.calculate_constraint_score(group)
    assert scores['regular'] == float('inf')  # No more regular capacity
   