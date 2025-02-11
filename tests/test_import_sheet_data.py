# Test the attributes of the shift constraints imported from the Google Sheet
import pytest
from app.scheduler.shift import Shift
from app.scheduler.shift_group import ShiftGroup

def test_shift_requirements_attributes(sample_shift_group_from_sheet):
    """
    Test the attributes of the shift constraints imported from the Google Sheet
    The shift constraints are imported from the Google Sheet and processed into a dictionary
    """
    # Assert that the shift group includes only a night shift on Last Saturday
    for shift in sample_shift_group_from_sheet.get_all_shifts_from_day("Last Saturday"):
        assert shift.shift_time == "Night"
    
    
    assert sample_shift_group_from_sheet.get_shift("Last Saturday", "Night").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Sunday", "Morning").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Sunday", "Noon").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Sunday", "Evening").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Sunday", "Night").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Monday", "Morning").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Monday", "Noon").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Monday", "Evening").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Monday", "Night").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Tuesday", "Morning").needed == 2
    assert sample_shift_group_from_sheet.get_shift("Tuesday", "Noon").needed == 4
    assert sample_shift_group_from_sheet.get_shift("Tuesday", "Evening").needed == 5
    assert sample_shift_group_from_sheet.get_shift("Tuesday", "Night").needed == 2
    assert sample_shift_group_from_sheet.get_shift("Wednesday", "Morning").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Wednesday", "Noon").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Wednesday", "Evening") is None
    assert sample_shift_group_from_sheet.get_shift("Wednesday", "Night").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Thursday", "Morning").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Thursday", "Noon").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Thursday", "Evening").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Thursday", "Night").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Friday", "Morning").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Friday", "Noon").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Friday", "Evening").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Friday", "Night").needed == 1
    assert sample_shift_group_from_sheet.get_shift("Saturday", "Morning").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Saturday", "Noon").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Saturday", "Evening").needed == 3
    assert sample_shift_group_from_sheet.get_shift("Saturday", "Night") is None

def test_person_attributes(sample_person_from_sheet):
    """Test the attributes of the Person object"""
    assert sample_person_from_sheet.name == "Random Person 1"
    assert sample_person_from_sheet.double_shift == False
    assert sample_person_from_sheet.max_shifts == 5
    assert sample_person_from_sheet.max_nights == 2
    assert sample_person_from_sheet.are_three_shifts_possible == False
    assert sample_person_from_sheet.night_and_noon_possible == True
    
    # Create a temporary group for comparison
    temp_group = ShiftGroup()
    expected_blocked_shifts = {
        ("Last Saturday", "Night"): True,
        ("Sunday", "Morning"): True,
        ("Monday", "Noon"): True,
        ("Tuesday", "Evening"): True,
        ("Wednesday", "Night"): True,
        ("Thursday", "Morning"): True,
        ("Friday", "Noon"): True,
        ("Saturday", "Evening"): True
    }
    
    # Debug prints
    print("\nExpected blocked shifts:")
    for day, time in expected_blocked_shifts:
        print(f"  {day} {time}")
    
    print("\nActual blocked shifts:")
    for (day, time), is_blocked in sample_person_from_sheet.blocked_shifts.items():
        if is_blocked:
            print(f"  {day} {time}")
        
    assert sample_person_from_sheet.blocked_shifts == expected_blocked_shifts
