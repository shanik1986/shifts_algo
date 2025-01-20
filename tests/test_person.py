import pytest
from app.scheduler.person import Person
from app.scheduler.shift import Shift, VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.shift_group import ShiftGroup


def test_shift_blocking(sample_person):
    """Test shift blocking using Shift objects"""
    # Test blocked shifts from each day of the week
    temp_group = ShiftGroup()  # Create temporary group for test shifts
    assert sample_person.is_shift_blocked(
        Shift("Last Saturday", "Night", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Sunday", "Morning", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Monday", "Noon", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Tuesday", "Evening", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Wednesday", "Night", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Thursday", "Morning", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Friday", "Noon", group=temp_group)) == True
    assert sample_person.is_shift_blocked(Shift("Saturday", "Evening", group=temp_group)) == True

    # Test available shifts from each day of the week
    assert sample_person.is_shift_blocked(Shift("Sunday", "Noon", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Monday", "Morning", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Tuesday", "Night", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Wednesday", "Evening", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Thursday", "Night", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Friday", "Morning", group=temp_group)) == False
    assert sample_person.is_shift_blocked(Shift("Saturday", "Noon", group=temp_group)) == False

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

def test_morning_after_night_constraint(sample_person, complete_shift_group):
    """Test morning after night constraint"""
    night_shift = Shift("Sunday", "Night", group=complete_shift_group)
    morning_shift = Shift("Monday", "Morning", group=complete_shift_group)
    # Assign night shift
    sample_person.assign_to_shift(night_shift)
    
    # Should not be eligible for morning shift next day
    assert complete_shift_group.is_morning_after_night(sample_person, morning_shift) == True
    assert sample_person.is_eligible_for_shift(morning_shift) == False

def test_night_before_morning_constraint(sample_person, complete_shift_group):
    """Test night before morning constraint"""
    # Assign morning shift
    sample_person.assign_to_shift(Shift("Monday", "Morning", group=complete_shift_group))
    
    # Testing that person is not eligible for night shift a day before the morning shift
    assert complete_shift_group.is_morning_after_night(sample_person, Shift("Sunday", "Night", group=complete_shift_group)) == True
    assert sample_person.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == False

def test_noon_after_night_constraint(sample_person_with_constraints, sample_person_with_no_constraints, complete_shift_group):
    """Test noon after night constraint"""
    # Testing that both people are eligible for night shift before the noon is assigned
    assert complete_shift_group.is_noon_after_night(sample_person_with_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == False
    assert complete_shift_group.is_noon_after_night(sample_person_with_no_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == False
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == True
    
    # Assign night shift
    sample_person_with_constraints.assign_to_shift(Shift("Sunday", "Night", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Sunday", "Night", group=complete_shift_group))
    
    # Testing that constrained person is not eligible for noon shift next day
    assert complete_shift_group.is_noon_after_night(sample_person_with_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False

    # Testing that unconstrained person is eligible for noon shift next day
    assert complete_shift_group.is_noon_after_night(sample_person_with_no_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == True

def test_night_before_noon_constraint(sample_person_with_constraints, sample_person_with_no_constraints, complete_shift_group):
    """Test night before noon constraint"""
    # Testing that both people are eligible for night shift before the noon is assigned
    assert complete_shift_group.is_noon_after_night(sample_person_with_constraints, Shift("Sunday", "Night", group=complete_shift_group)) == False
    assert complete_shift_group.is_noon_after_night(sample_person_with_no_constraints, Shift("Sunday", "Night", group=complete_shift_group)) == False
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == True
    
    # Assign noon shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    
    #Testing that constrained person is not eligible for night shift the day before
    assert complete_shift_group.is_noon_after_night(sample_person_with_constraints, Shift("Sunday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == False

    #Testing that unconstrained person is eligible for night shift the day before
    assert complete_shift_group.is_noon_after_night(sample_person_with_no_constraints, Shift("Sunday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == True

def test_night_after_evening_constraint(sample_person, complete_shift_group):
    """Test night after evening constraint"""
    # Assign evening shift
    sample_person.assign_to_shift(Shift("Sunday", "Evening", group=complete_shift_group))
    
    # Should not be eligible for night shift same day
    assert complete_shift_group.is_night_after_evening(sample_person, Shift("Sunday", "Night", group=complete_shift_group)) == True
    assert sample_person.is_eligible_for_shift(Shift("Sunday", "Night", group=complete_shift_group)) == False

def test_evening_before_night_constraint(sample_person, complete_shift_group):
    """Test evening before night constraint"""
    # Assign night shift
    sample_person.assign_to_shift(Shift("Sunday", "Night", group=complete_shift_group))
    
    # Should not be eligible for evening shift same day
    assert complete_shift_group.is_night_after_evening(sample_person, Shift("Sunday", "Evening", group=complete_shift_group)) == True
    assert sample_person.is_eligible_for_shift(Shift("Sunday", "Evening", group=complete_shift_group)) == False

def test_consecutive_shifts_constraint(sample_person_with_constraints, sample_person_with_no_constraints, complete_shift_group):
    """Test consecutive shifts constraint for person with constraints and for person with no constraints"""
    # Assert that both people are eligible for all shifts and that no shift triggers the consecutive shift constraint
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        assert sample_person_with_constraints.is_eligible_for_shift(shift) == True
        assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True
        assert complete_shift_group.is_consecutive_shift(sample_person_with_constraints, shift) == False
        assert complete_shift_group.is_consecutive_shift(sample_person_with_no_constraints, shift) == False
    
    # Assign morning shifts for each week day to both people
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_morning:
            sample_person_with_constraints.assign_to_shift(shift)
            sample_person_with_no_constraints.assign_to_shift(shift)
    
    # Validate that the constrained person is not eligible for the noon shift any weekday and that the unconstrained person is eligible
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_noon:
            assert complete_shift_group.is_consecutive_shift(sample_person_with_constraints, shift) == True
            assert sample_person_with_constraints.is_eligible_for_shift(shift) == False
            assert complete_shift_group.is_consecutive_shift(sample_person_with_no_constraints, shift) == True
            assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True

    # Unassign both person from morning shifts
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_morning:
            sample_person_with_constraints.unassign_from_shift(shift)
            sample_person_with_no_constraints.unassign_from_shift(shift)

    # Assign both people for Noon shifts every day of the week
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_noon:
            sample_person_with_constraints.assign_to_shift(shift)
            sample_person_with_no_constraints.assign_to_shift(shift)

    # Validate that the constrained person is not eligible for the evening shift any weekday and that the unconstrained person is eligible
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_evening:
            assert complete_shift_group.is_consecutive_shift(sample_person_with_constraints, shift) == True
            assert sample_person_with_constraints.is_eligible_for_shift(shift) == False
            assert complete_shift_group.is_consecutive_shift(sample_person_with_no_constraints, shift) == True
            assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True

    # Validate that the constrained person is not eligible for the morning shift any weekday and that the unconstrained person is eligible
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_morning:
            assert complete_shift_group.is_consecutive_shift(sample_person_with_constraints, shift) == True
            assert sample_person_with_constraints.is_eligible_for_shift(shift) == False
            assert complete_shift_group.is_consecutive_shift(sample_person_with_no_constraints, shift) == True
            assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True

    # Unassign both people from Noon shifts
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_noon:
            sample_person_with_constraints.unassign_from_shift(shift)
            sample_person_with_no_constraints.unassign_from_shift(shift)

    # Assign both people for Evening shifts every day of the week + Assigning to Friday Evening
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_evening:
            sample_person_with_constraints.assign_to_shift(shift)
            sample_person_with_no_constraints.assign_to_shift(shift)
    sample_person_with_constraints.assign_to_shift(Shift("Friday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Friday", "Evening", group=complete_shift_group))

    # Validate that the constrained person is eligible for the noon shift any weekday and that the unconstrained person is eligible
    for shift in Shift.create_weekday_shifts(complete_shift_group):
        if shift.is_noon:
            assert complete_shift_group.is_consecutive_shift(sample_person_with_constraints, shift) == True
            assert sample_person_with_constraints.is_eligible_for_shift(shift) == False
            assert complete_shift_group.is_consecutive_shift(sample_person_with_no_constraints, shift) == True
            assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True

def test_three_shifts_constraint(sample_person_with_constraints, sample_person_with_no_constraints, complete_shift_group):
    """Test three shifts constraint"""

    # Assert that both people are eligible to all of Monday's shifts and don't trigger the three shifts constraint
    for shift in complete_shift_group.get_all_shifts_from_day("Monday"):
        assert sample_person_with_constraints.is_eligible_for_shift(shift) == True
        assert complete_shift_group.is_third_shift(sample_person_with_constraints, shift) == False

        assert sample_person_with_no_constraints.is_eligible_for_shift(shift) == True
        assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, shift) == False
    
    """
    Morning + Noon are assigned: Testing evening and night shift
    """
    # Assign morning and noon shifts on Monday
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Morning", group=complete_shift_group))
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Morning", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    
    # Assert that person with constraints is not eligible for evening and night shifts
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    
    # Assert that person with no constraints is eligible for night shift but not eligible for evening shift becuase he can't do 3 shifts in a row
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == True

    # Unassign noon shift
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Noon", group=complete_shift_group))

    """
    Morning + Evening are assigned: Testing noon and night shift
    """
    # Assign evening shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))
    
    # Assert that person with constraints is not eligible for noon and night shifts
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == False

    # Assert that person with no constraints is not eligible for noon and night shifts because he can't do evening and night in a row
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == False

    # Unassign evening shift
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Evening", group=complete_shift_group))

    """
    Morning + Night are assigned: Testing evening and noon shift
    """ 

    # Assign night shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Night", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Night", group=complete_shift_group))
    
    # Assert that person with constraints is not eligible for evening and night shift
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False

    # Assert that person with no constraints is not eligible for evening shift but eligible for night shift
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == True
    
    # Unassign morning and night shift
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Morning", group=complete_shift_group))
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Night", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Morning", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Night", group=complete_shift_group))

    """
    Noon + Evening are assigned: Testing morning and night shift
    """

    # Assign noon and evening shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))

    # Assert that person with constraints is not eligible for morning and night shift
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == False

    # Assert that person with no constraints is not eligible for morning and night shift
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Night", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Night", group=complete_shift_group)) == False

    # Unassign evening shift
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Evening", group=complete_shift_group))

    """
    Noon + Night are assigned: Testing morning and evening shift
    """

    # Assign night shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Night", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Night", group=complete_shift_group))

    # Assert that person with constraints is not eligible for morning and evening shift
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False

    # Assert that person with no constraints is eligible for morning but not eligible for evening shift
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Evening", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Evening", group=complete_shift_group)) == False
    
    # Unassign Noon shift
    sample_person_with_constraints.unassign_from_shift(Shift("Monday", "Noon", group=complete_shift_group))
    sample_person_with_no_constraints.unassign_from_shift(Shift("Monday", "Noon", group=complete_shift_group))

    """
    Evening + Night are assigned: Testing morning and noon shift
    """
    
    # Assign evening shift
    sample_person_with_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))
    sample_person_with_no_constraints.assign_to_shift(Shift("Monday", "Evening", group=complete_shift_group))  

    # Assert that person with constraints is not eligible for morning and noon shift
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False
    
    # Assert that person with no constraints is not eligible for morning and noon shift
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Morning", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Morning", group=complete_shift_group)) == False
    assert complete_shift_group.is_third_shift(sample_person_with_no_constraints, Shift("Monday", "Noon", group=complete_shift_group)) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift(Shift("Monday", "Noon", group=complete_shift_group)) == False

def test_calculate_constraint_score(sample_person):
    
    """
    Test constraint score calculation.
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
    
    # From the remaining shifts, the person is eligibile for Sunday Noon and Monday Evening
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
    
    # assignments = {
    #     "Friday": {"Morning": [], "Noon": [], "Evening": [], "Night": []},
    #     "Saturday": {"Morning": [], "Noon": [], "Evening": [], "Night": []}
    # }
    
    # First weekend shift should be allowed
    assert person.is_eligible_for_shift(Shift("Friday", "Evening", group=complete_shift_group)) == True
    person.assign_to_shift(Shift("Friday", "Evening", group=complete_shift_group))
    
    # Second weekend shift should not be allowed
    assert person.is_eligible_for_shift(Shift("Saturday", "Morning", group=complete_shift_group)) == False
    
    # Unassigning should make weekend shifts available again
    person.unassign_from_shift(Shift("Friday", "Evening", group=complete_shift_group))
    assert person.is_eligible_for_shift(Shift("Saturday", "Morning", group=complete_shift_group)) == True 