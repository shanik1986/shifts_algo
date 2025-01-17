import pandas as pd
from app.google_sheets.init_sheet_access import get_google_sheet_data
from app.scheduler.constants import DAYS, SHIFTS
import sys
from app.scheduler.person import Person

# Parse the dataset into a structured format
def parse_shift_constraints(df):
    # Fix the boolean columns to ensure proper booleans
    boolean_columns = ["Double Shifts?", "3 Shift Days?", "Night + Noon"]
    for col in boolean_columns:
        df[col] = df[col].astype(str).str.strip().str.upper() == "TRUE"

    processed_data = []
    for _, row in df.iterrows():
        unavailable = []
        column_index = 9  # Start with "Last Saturday Night"

        # Loop through days and shifts
        for day in DAYS:
            for shift in SHIFTS:
                # Skip non-existing shifts for Last Saturday (only Night exists)
                if day == "Last Saturday" and shift != "Night":
                    continue

                availability = row.iloc[column_index]
                if str(availability).strip().upper() == "FALSE":
                    unavailable.append((day, shift))
                column_index += 1

        # Create Person object but convert to dict to maintain compatibility
        person = Person(
            name=row["Name"],
            unavailable=unavailable,
            double_shift=row["Double Shifts?"],
            max_shifts=int(row["Max Shifts"]),
            max_nights=int(row["Max Nights"]),
            are_three_shifts_possible=row["3 Shift Days?"],
            night_and_noon_possible=row["Night + Noon"],
            shift_counts=0,  # Initialize to 0
            night_counts=0   # Initialize to 0
        )
        
        # Temporarily convert back to dict to maintain compatibility
        person_dict = {
            "name": person.name,
            "unavailable": person.unavailable,
            "double_shift": person.double_shift,
            "max_shifts": person.max_shifts,
            "max_nights": person.max_nights,
            "are_three_shifts_possible": person.are_three_shifts_possible,
            "night_and_noon_possible": person.night_and_noon_possible
        }
        processed_data.append(person_dict)
    
    return processed_data

def parse_shift_requirements(df):
    day_column = df.columns[0]
    shifts_per_day = {}
    for index, row in df.iterrows():
        day = row[day_column]  
        shifts_per_day[day] = {}
        
        # Iterate through shifts and their corresponding values
        for shift in SHIFTS:
            if pd.notnull(row[shift]) and row[shift] > 0:  # Include only non-null and positive values
                shifts_per_day[day][shift] = int(row[shift])
    
    return shifts_per_day

# Add this function to get fresh data
def get_fresh_data():
    """
    Gets fresh data from Google Sheets and processes it
    Returns: (shift_constraints, shift_requirements)
    """
    shift_constraint_data = get_google_sheet_data("Shifts", "Real Data - 15/01")
    shift_requirements_data = get_google_sheet_data("Shifts", "Needed Shifts")
    
    shift_constraints = parse_shift_constraints(shift_constraint_data)
    shift_requirements = parse_shift_requirements(shift_requirements_data)
    
    return shift_constraints, shift_requirements

# print(shift_requirements)
# print(structured_data)