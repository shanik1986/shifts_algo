import pandas as pd
from app.google_sheets.init_sheet_access import get_google_sheet_data
from app.scheduler.constants import DAYS, SHIFTS
import sys
from app.scheduler.person import Person
from app.scheduler.shift import Shift, VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.shift_group import ShiftGroup

def create_shift_group_from_requirements(df) -> ShiftGroup:
    """Create a ShiftGroup with all shifts from requirements"""
    shift_group = ShiftGroup()
    
    for _, row in df.iterrows():
        day = row[df.columns[0]]  # First column is the day
        for shift_time in SHIFTS:
            if pd.notnull(row[shift_time]) and row[shift_time] > 0:
                shift = Shift(day, shift_time, needed=int(row[shift_time]))
                shift_group.add_shift(shift)
    
    return shift_group

def parse_shift_constraints(df, shift_group: ShiftGroup):
    """Parse shift constraints using existing shifts from ShiftGroup"""
    # Fix the boolean columns
    boolean_columns = ["Double Shifts?", "3 Shift Days?", "Night + Noon"]
    for col in boolean_columns:
        df[col] = df[col].astype(str).str.strip().str.upper() == "TRUE"

    processed_data = []
    for _, row in df.iterrows():
        unavailable = []
        
        # Get availability from column names
        for day in VALID_DAYS:
            for time in VALID_SHIFT_TIMES:
                column_name = f"{day} {time}"  # Column names in sheet match "Day Time" format
                if column_name in df.columns:  # Only check if column exists
                    if str(row[column_name]).strip().upper() == "FALSE":
                        shift = shift_group.get_shift(day, time)
                        if shift:
                            unavailable.append(shift)

        # Create Person object
        person = Person(
            name=row["Name"],
            unavailable=unavailable,
            double_shift=row["Double Shifts?"],
            max_shifts=int(row["Max Shifts"]),
            max_nights=int(row["Max Nights"]),
            are_three_shifts_possible=row["3 Shift Days?"],
            night_and_noon_possible=row["Night + Noon"],
            shift_counts=0,
            night_counts=0
        )
        
        processed_data.append(person)
    
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

def get_fresh_data():
    """
    Gets fresh data from Google Sheets and processes it
    Returns: shift_group, people
    """
    shift_requirements_data = get_google_sheet_data("Shifts", "Needed Shifts")
    shift_constraint_data = get_google_sheet_data("Shifts", "Real Data - 15/01")
    
    # First create shift group from requirements
    shift_group = create_shift_group_from_requirements(shift_requirements_data)
    
    # Then parse constraints using the existing shifts
    people = parse_shift_constraints(shift_constraint_data, shift_group)
    
    return shift_group, people

# print(shift_requirements)
# print(structured_data)