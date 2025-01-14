from app.google_sheets.import_sheet_data import shift_requirements

def compare_shifts_data(parsed_data, reference_data):
    """
    Compares two dictionaries representing shifts_per_day to ensure they match.

    Args:
        parsed_data (dict): The dictionary parsed from the imported data.
        reference_data (dict): The reference dictionary to compare against.

    Returns:
        bool: True if the dictionaries match, False otherwise.
    """
    import pprint

    if parsed_data == reference_data:
        print("✅ The parsed data matches the reference data!")
        return True
    else:
        print("❌ The parsed data does not match the reference data.")
        print("\nDifferences:")
        
        # Compare keys
        for day in reference_data.keys():
            if day not in parsed_data:
                print(f"- Missing day in parsed data: {day}")
            elif parsed_data[day] != reference_data[day]:
                print(f"- Mismatch for {day}:")
                print("  Parsed data:")
                pprint.pprint(parsed_data[day])
                print("  Reference data:")
                pprint.pprint(reference_data[day])

        # Check for additional days in parsed data
        for day in parsed_data.keys():
            if day not in reference_data:
                print(f"- Additional day in parsed data: {day}")

        return False

shifts_per_day = {
    
   "Last Saturday": {"Night": 3},
   "Sunday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
    "Monday": {"Morning": 0, "Noon": 0, "Evening": 0, "Night": 3},
    "Tuesday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
    "Wednesday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
    "Thursday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
   "Friday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
    "Saturday": {"Morning": 3, "Noon": 3, "Evening": 3},
}

compare_shifts_data(shift_requirements, shifts_per_day)