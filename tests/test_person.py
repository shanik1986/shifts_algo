from app.scheduler.person import Person
from app.scheduler.constants import DAYS, SHIFTS

def test_person_attributes(sample_person_from_sheet):
    """Test the attributes of the Person object"""
    assert sample_person_from_sheet.name == "Random Person 1"
    assert sample_person_from_sheet.double_shift == False
    assert sample_person_from_sheet.max_shifts == 5
    assert sample_person_from_sheet.max_nights == 2
    assert sample_person_from_sheet.are_three_shifts_possible == False
    assert sample_person_from_sheet.night_and_noon_possible == True
    assert sample_person_from_sheet.unavailable == [
        ("Last Saturday", "Night"),
        ("Sunday", "Morning"),
        ("Monday", "Noon"),
        ("Tuesday", "Evening"),
        ("Wednesday", "Night"),
        ("Thursday", "Morning"),
        ("Friday", "Noon"),
        ("Saturday", "Evening")
        ]
    assert sample_person_from_sheet.shift_counts == 0
    assert sample_person_from_sheet.night_counts == 0
    assert sample_person_from_sheet.constraints_score == 0

def test_shift_blocking(sample_person_from_sheet):

    # Test a blocked shift from each day of the week
    assert sample_person_from_sheet.is_shift_blocked("Last Saturday", "Night") == True
    assert sample_person_from_sheet.is_shift_blocked("Sunday", "Morning") == True
    assert sample_person_from_sheet.is_shift_blocked("Monday", "Noon") == True
    assert sample_person_from_sheet.is_shift_blocked("Tuesday", "Evening") == True
    assert sample_person_from_sheet.is_shift_blocked("Wednesday", "Night") == True
    assert sample_person_from_sheet.is_shift_blocked("Thursday", "Morning") == True
    assert sample_person_from_sheet.is_shift_blocked("Friday", "Noon") == True
    assert sample_person_from_sheet.is_shift_blocked("Saturday", "Evening") == True

    # Test an available shift from each day of the week
    assert sample_person_from_sheet.is_shift_blocked("Sunday", "Noon") == False
    assert sample_person_from_sheet.is_shift_blocked("Monday", "Morning") == False
    assert sample_person_from_sheet.is_shift_blocked("Tuesday", "Night") == False
    assert sample_person_from_sheet.is_shift_blocked("Wednesday", "Evening") == False
    assert sample_person_from_sheet.is_shift_blocked("Thursday", "Night") == False
    assert sample_person_from_sheet.is_shift_blocked("Friday", "Morning") == False
    assert sample_person_from_sheet.is_shift_blocked("Saturday", "Noon") == False

def test_person_conversion(sample_person_dict_from_sheet):
    """Test conversion between dictionary and Person object"""
    # Convert dict to Person
    person = Person.from_dict(sample_person_dict_from_sheet)
    
    # Test that all attributes are correctly converted
    assert person.name == sample_person_dict_from_sheet["name"]
    assert person.unavailable == sample_person_dict_from_sheet["unavailable"]
    assert person.double_shift == sample_person_dict_from_sheet["double_shift"]
    assert person.max_shifts == sample_person_dict_from_sheet["max_shifts"]
    assert person.max_nights == sample_person_dict_from_sheet["max_nights"]
    assert person.are_three_shifts_possible == sample_person_dict_from_sheet["are_three_shifts_possible"]
    assert person.night_and_noon_possible == sample_person_dict_from_sheet["night_and_noon_possible"]
    assert person.shift_counts == 0
    assert person.night_counts == 0
    assert person.constraints_score == 0

def test_shift_assignment_and_unassignment(sample_person_from_sheet, sample_current_assignments):
    #Assign person to a shift
    sample_person_from_sheet.assign_to_shift("Sunday", "Noon", sample_current_assignments)
    assert sample_person_from_sheet.shift_counts == 1
    assert sample_person_from_sheet.night_counts == 0

    #Unassign person from a shift
    sample_person_from_sheet.unassign_from_shift("Sunday", "Noon", sample_current_assignments)
    assert sample_person_from_sheet.shift_counts == 0
    assert sample_person_from_sheet.night_counts == 0

def test_night_assignment_and_unassignment(sample_person_from_sheet, sample_current_assignments):
    #Assign person to a night
    sample_person_from_sheet.assign_to_shift("Sunday", "Night", sample_current_assignments)
    assert sample_person_from_sheet.shift_counts == 1
    assert sample_person_from_sheet.night_counts == 1

    #Unassign person from a night
    sample_person_from_sheet.unassign_from_shift("Sunday", "Night", sample_current_assignments)
    assert sample_person_from_sheet.shift_counts == 0
    assert sample_person_from_sheet.night_counts == 0

def test_max_shifts_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test max shifts constraint"""
    # Assign up to max shifts
    for i in range(sample_person_from_sheet.max_shifts):
        assert sample_person_from_sheet.is_max_shifts_reached() == False
        sample_person_from_sheet.assign_to_shift("Sunday", "Noon", sample_current_assignments)
    
    assert sample_person_from_sheet.is_max_shifts_reached() == True
    sample_person_from_sheet.unassign_from_shift("Sunday", "Noon", sample_current_assignments)
    assert sample_person_from_sheet.is_max_shifts_reached() == False

def test_max_nights_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test max nights constraint"""
    # Assign up to max nights
    for i in range(sample_person_from_sheet.max_nights):
        assert sample_person_from_sheet.is_max_nights_reached() == False
        sample_person_from_sheet.assign_to_shift("Sunday", "Night", sample_current_assignments)
        
    
    assert sample_person_from_sheet.is_max_nights_reached() == True
    assert sample_person_from_sheet.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False
    sample_person_from_sheet.unassign_from_shift("Sunday", "Night", sample_current_assignments)
    assert sample_person_from_sheet.is_max_nights_reached() == False

def test_morning_after_night_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test morning after night constraint"""
    # Assign night shift
    sample_person_from_sheet.assign_to_shift("Sunday", "Night", sample_current_assignments)
    
    # Should not be eligible for morning shift next day
    assert sample_person_from_sheet.is_morning_after_night("Monday", "Morning", sample_current_assignments) == True
    assert sample_person_from_sheet.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False

def test_night_before_morning_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test night before morning constraint"""
    # Assign morning shift
    sample_person_from_sheet.assign_to_shift("Monday", "Morning", sample_current_assignments)
    
    # Testing that person is not eligible for night shift next day
    assert sample_person_from_sheet.is_morning_after_night("Sunday", "Night", sample_current_assignments) == True
    assert sample_person_from_sheet.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == False

def test_noon_after_night_constraint(sample_person_with_constraints, sample_person_with_no_constraints, sample_current_assignments):
    """Test noon after night constraint"""
    # Testing that both people are eligible for night shift before the noon is assigned
    assert sample_person_with_constraints.is_noon_after_night("Monday", "Noon", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_noon_after_night("Monday", "Noon", sample_current_assignments) == False
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == True
    
    # Assign night shift
    sample_person_with_constraints.assign_to_shift("Sunday", "Night", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Sunday", "Night", sample_current_assignments)
    
    # Testing that constrained person is not eligible for noon shift next day
    assert sample_person_with_constraints.is_noon_after_night("Monday", "Noon", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == False

    # Testing that unconstrained person is eligible for noon shift next day
    assert sample_person_with_no_constraints.is_noon_after_night("Monday", "Noon", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == True

def test_night_before_noon_constraint(sample_person_with_constraints, sample_person_with_no_constraints, sample_current_assignments):
    """Test night before noon constraint"""
    # Testing that both people are eligible for night shift before the noon is assigned
    assert sample_person_with_constraints.is_noon_after_night("Sunday", "Night", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_noon_after_night("Sunday", "Night", sample_current_assignments) == False
    assert sample_person_with_constraints.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == True
    
    # Assign noon shift
    sample_person_with_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    
    #Testing that constrained person is not eligible for night shift the day before
    assert sample_person_with_constraints.is_noon_after_night("Sunday", "Night", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == False

    #Testing that unconstrained person is eligible for night shift the day before
    assert sample_person_with_no_constraints.is_noon_after_night("Sunday", "Night", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == True

def test_night_after_evening_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test night after evening constraint"""
    # Assign evening shift
    sample_person_from_sheet.assign_to_shift("Sunday", "Evening", sample_current_assignments)
    
    # Should not be eligible for night shift same day
    assert sample_person_from_sheet.is_night_after_evening("Sunday", "Night", sample_current_assignments) == True
    assert sample_person_from_sheet.is_eligible_for_shift("Sunday", "Night", sample_current_assignments) == False

def test_evening_before_night_constraint(sample_person_from_sheet, sample_current_assignments):
    """Test evening before night constraint"""
    # Assign night shift
    sample_person_from_sheet.assign_to_shift("Sunday", "Night", sample_current_assignments)
    
    # Should not be eligible for evening shift same day
    assert sample_person_from_sheet.is_night_after_evening("Sunday", "Evening", sample_current_assignments) == True
    assert sample_person_from_sheet.is_eligible_for_shift("Sunday", "Evening", sample_current_assignments) == False

def test_consecutive_shifts_constraint(sample_person_with_constraints, sample_person_with_no_constraints, sample_current_assignments):
    """Test consecutive shifts constraint for person with constraints and for person with no constraints"""
    # Assert that both people are eligible for all shifts and that no shift triggers the consecutive shift constraint
    for day in DAYS:
        for shift in SHIFTS:
            assert sample_person_with_constraints.is_eligible_for_shift(day, shift, sample_current_assignments) == True
            assert sample_person_with_no_constraints.is_eligible_for_shift(day, shift, sample_current_assignments) == True
            assert sample_person_with_constraints.is_consequtive_shift(day, shift, sample_current_assignments) == False
            assert sample_person_with_no_constraints.is_consequtive_shift(day, shift, sample_current_assignments) == False
    
    # Assign morning shifts for each day of the week to both people
    for day in DAYS:
        sample_person_with_constraints.assign_to_shift(day, "Morning", sample_current_assignments)
        sample_person_with_no_constraints.assign_to_shift(day, "Morning", sample_current_assignments)
    
    # Validate that the constrained person is not eligible for the noon shift any day of the week and that the unconstrained person is eligible
    for day in DAYS:
        assert sample_person_with_constraints.is_consequtive_shift(day, "Noon", sample_current_assignments) == True
        assert sample_person_with_constraints.is_eligible_for_shift(day, "Noon", sample_current_assignments) == False
        assert sample_person_with_no_constraints.is_consequtive_shift(day, "Noon", sample_current_assignments) == True
        assert sample_person_with_no_constraints.is_eligible_for_shift(day, "Noon", sample_current_assignments) == True

    # Unassign both person from morning shifts
    for day in DAYS:
        sample_person_with_constraints.unassign_from_shift(day, "Morning", sample_current_assignments)
        sample_person_with_no_constraints.unassign_from_shift(day, "Morning", sample_current_assignments)

    # Assign both people for Noon shifts every day of the week
    for day in DAYS:
        sample_person_with_constraints.assign_to_shift(day, "Noon", sample_current_assignments)
        sample_person_with_no_constraints.assign_to_shift(day, "Noon", sample_current_assignments)

    # Validate that the constrained person is not eligible for the evening shift any day of the week and that the unconstrained person is eligible
    for day in DAYS:
        assert sample_person_with_constraints.is_consequtive_shift(day, "Evening", sample_current_assignments) == True
        assert sample_person_with_constraints.is_eligible_for_shift(day, "Evening", sample_current_assignments) == False
        assert sample_person_with_no_constraints.is_consequtive_shift(day, "Evening", sample_current_assignments) == True
        assert sample_person_with_no_constraints.is_eligible_for_shift(day, "Evening", sample_current_assignments) == True

    # Validate that the constrained person is not eligible for the morning shift any day of the week and that the unconstrained person is eligible
    for day in DAYS:
        assert sample_person_with_constraints.is_consequtive_shift(day, "Morning", sample_current_assignments) == True
        assert sample_person_with_constraints.is_eligible_for_shift(day, "Morning", sample_current_assignments) == False
        assert sample_person_with_no_constraints.is_consequtive_shift(day, "Morning", sample_current_assignments) == True
        assert sample_person_with_no_constraints.is_eligible_for_shift(day, "Morning", sample_current_assignments) == True

    # Unassign both people from Noon shifts
    for day in DAYS:
        sample_person_with_constraints.unassign_from_shift(day, "Noon", sample_current_assignments)
        sample_person_with_no_constraints.unassign_from_shift(day, "Noon", sample_current_assignments)

    # Assign both people for Evening shifts every day of the week
    for day in DAYS:
        sample_person_with_constraints.assign_to_shift(day, "Evening", sample_current_assignments)
        sample_person_with_no_constraints.assign_to_shift(day, "Evening", sample_current_assignments)

    # Validate that the constrained person is eligible for the noon shift any day of the week and that the unconstrained person is eligible
    for day in DAYS:
        assert sample_person_with_constraints.is_consequtive_shift(day, "Noon", sample_current_assignments) == True
        assert sample_person_with_constraints.is_eligible_for_shift(day, "Noon", sample_current_assignments) == False
        assert sample_person_with_no_constraints.is_consequtive_shift(day, "Noon", sample_current_assignments) == True
        assert sample_person_with_no_constraints.is_eligible_for_shift(day, "Noon", sample_current_assignments) == True

def test_three_shifts_constraint(sample_person_with_constraints, sample_person_with_no_constraints, sample_current_assignments):
    """Test three shifts constraint"""

    # Assert that person is eligible to all shifts on Monday and that none of them trigger the three shifts constraint
    for shift in SHIFTS:
        assert sample_person_with_constraints.is_eligible_for_shift("Monday", shift, sample_current_assignments) == True
        assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == False

        assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", shift, sample_current_assignments) == True
        assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == False
    
    """
    Morning + Noon are assigned: Testing evening and night shift
    """
    # Assign morning and noon shifts
    sample_person_with_constraints.assign_to_shift("Monday", "Morning", sample_current_assignments)
    sample_person_with_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Morning", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    
    # Assert that person with constraints is not eligible for evening and night shifts
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False
    
    # Assert that person with no constraints is eligible for night shift but not eligible for evening shift becuase he can't do 3 shifts in a row
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == True

    # Unassign noon shift
    sample_person_with_constraints.unassign_from_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Noon", sample_current_assignments)

    """
    Morning + Evening are assigned: Testing noon and night shift
    """
    # Assign evening shift
    sample_person_with_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)
    
    # Assert that person with constraints is not eligible for noon and night shifts
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False

    # Assert that person with no constraints is not eligible for noon and night shifts because he can't do evening and night in a row
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False

    # Unassign evening shift
    sample_person_with_constraints.unassign_from_shift("Monday", "Evening", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Evening", sample_current_assignments)

    """
    Morning + Night are assigned: Testing evening and noon shift
    """ 

    # Assign night shift
    sample_person_with_constraints.assign_to_shift("Monday", "Night", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Night", sample_current_assignments)
    
    # Assert that person with constraints is not eligible for evening and night shift
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False

    # Assert that person with no constraints is not eligible for evening shift but eligible for night shift
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == True
    
    # Unassign morning and night shift
    sample_person_with_constraints.unassign_from_shift("Monday", "Morning", sample_current_assignments)
    sample_person_with_constraints.unassign_from_shift("Monday", "Night", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Morning", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Night", sample_current_assignments)

    """
    Noon + Evening are assigned: Testing morning and night shift
    """

    # Assign noon and evening shift
    sample_person_with_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)

    # Assert that person with constraints is not eligible for morning and night shift
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False

    # Assert that person with no constraints is not eligible for morning and night shift
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Night", sample_current_assignments) == False

    # Unassign evening shift
    sample_person_with_constraints.unassign_from_shift("Monday", "Evening", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Evening", sample_current_assignments)

    """
    Noon + Night are assigned: Testing morning and evening shift
    """

    # Assign night shift
    sample_person_with_constraints.assign_to_shift("Monday", "Night", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Night", sample_current_assignments)

    # Assert that person with constraints is not eligible for morning and evening shift
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False

    # Assert that person with no constraints is eligible for morning but not eligible for evening shift
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Evening", sample_current_assignments) == False
    
    # Unassign Noon shift
    sample_person_with_constraints.unassign_from_shift("Monday", "Noon", sample_current_assignments)
    sample_person_with_no_constraints.unassign_from_shift("Monday", "Noon", sample_current_assignments)

    """
    Evening + Night are assigned: Testing morning and noon shift
    """
    
    # Assign evening shift
    sample_person_with_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)
    sample_person_with_no_constraints.assign_to_shift("Monday", "Evening", sample_current_assignments)  
    
    # Assert that person with constraints is not eligible for morning and noon shift
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False
    assert sample_person_with_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == False
    
    # Assert that person with no constraints is not eligible for morning and noon shift
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Morning", sample_current_assignments) == False
    assert sample_person_with_no_constraints.is_third_shift("Monday", sample_current_assignments) == True
    assert sample_person_with_no_constraints.is_eligible_for_shift("Monday", "Noon", sample_current_assignments) == False

def test_calculate_constraint_score(sample_person_from_sheet, sample_current_assignments):
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
    #Assign to Sunday Night
    sample_person_from_sheet.assign_to_shift("Sunday", "Night", sample_current_assignments)
    
    # From the remaining shifts, the person is eligibile for Sunday Noon and Monday Evening
    remaining_shifts = [
        ("Sunday", "Morning", 2),
        ("Sunday", "Noon", 2),
        ("Sunday", "Evening", 2),
        ("Monday", "Morning", 2),
        ("Monday", "Evening", 2)
    ]

    # Calculate initial constraint score
    assert sample_person_from_sheet.calculate_constraint_score(
        remaining_shifts, sample_current_assignments) == 0.5
    
    
    # Assign to Monday evening to reduce constraint score
    sample_person_from_sheet.assign_to_shift("Monday", "Evening", sample_current_assignments)
    remaining_shifts.remove(("Monday", "Evening", 2))
    
    # Calculate new constraint score
    assert sample_person_from_sheet.calculate_constraint_score(
        remaining_shifts, sample_current_assignments) == (1/3)
    
    # Assign to Thursday morning, Saturday morning and Saturday night to make the person completely unavailable
    sample_person_from_sheet.assign_to_shift("Saturday", "Morning", sample_current_assignments)
    assert sample_person_from_sheet.calculate_constraint_score(
        remaining_shifts, sample_current_assignments) == (1/2)
    
    sample_person_from_sheet.assign_to_shift("Saturday", "Night", sample_current_assignments)
    assert sample_person_from_sheet.calculate_constraint_score(
        remaining_shifts, sample_current_assignments) == (1)
    
    sample_person_from_sheet.assign_to_shift("Thursday", "Morning", sample_current_assignments)
    assert sample_person_from_sheet.calculate_constraint_score(
        remaining_shifts, sample_current_assignments) == float("inf")
