from app.google_sheets.import_sheet_data import get_google_sheet_data, create_shift_group_from_requirements, parse_shift_constraints

def test_itay_constraints():
    # Get the data
    shift_requirements_data = get_google_sheet_data("Shifts", "Needed Shifts")
    shift_constraint_data = get_google_sheet_data("Shifts", "Real Data - 15/01")
    
    # Print column names
    print("\nAvailable columns in the spreadsheet:")
    for col in shift_constraint_data.columns:
        print(f"- {col}")
    
    # Create shift group
    shift_group = create_shift_group_from_requirements(shift_requirements_data)
    
    # Filter for just Itay's data
    itay_data = shift_constraint_data[shift_constraint_data['Name'] == 'Itay']
    
    if itay_data.empty:
        print("Could not find Itay in the data!")
        return
    
    # Print Itay's entire row
    print("\nItay's raw data:")
    print(itay_data.iloc[0])
    
    # Process constraints
    print("\nProcessing constraints:")
    people = parse_shift_constraints(itay_data, shift_group)
    
    if people:
        itay = people[0]
        print("\nFinal unavailable shifts:")
        for shift in itay.unavailable:
            print(f"- {shift.shift_day} {shift.shift_time}")

if __name__ == "__main__":
    test_itay_constraints() 