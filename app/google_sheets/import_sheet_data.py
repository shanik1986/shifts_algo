import pandas as pd
from app.google_sheets.init_sheet_access import get_google_sheet_data
import sys

# Define days and shifts
DAYS = ["Last Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SHIFTS = ["Morning", "Noon", "Evening", "Night"]

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

        # Structure for each person
        person = {
            "name": row["Name"],
            "double_shift": row["Double Shifts?"],
            "max_shifts": int(row["Max Shifts"]),
            "max_nights": int(row["Max Nights"]),
            "are_three_shifts_possible": row["3 Shift Days?"],
            "night_and_noon_possible": row["Night + Noon"],
            "unavailable": unavailable
        }
        processed_data.append(person)
    
    return processed_data

def parse_shift_requirements(df):
    day_column = df.columns[0]
    shifts_per_day = {}
    for index, row in df.iterrows():
        day = row[day_column]  
        shifts_per_day[day] = {}
        
        # Iterate through shifts and their corresponding values
        for shift in ["Morning", "Noon", "Evening", "Night"]:
            if pd.notnull(row[shift]) and row[shift] > 0:  # Include only non-null and positive values
                shifts_per_day[day][shift] = int(row[shift])
    
    return shifts_per_day



# Define sheet parameters
shift_constraint_data = get_google_sheet_data("Shifts", "Real Data - 15/01")
shift_requirements_data = get_google_sheet_data("Shifts", "Needed Shifts")

# Process the datasets
shift_constraints = parse_shift_constraints(shift_constraint_data)
shift_requirements = parse_shift_requirements(shift_requirements_data)



# print(shift_requirements)
# print(structured_data)