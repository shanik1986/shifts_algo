from app.scheduler.person import Person

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
