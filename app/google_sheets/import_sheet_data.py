import pandas as pd
from app.google_sheets.init_sheet_access import get_google_sheet_data
from app.scheduler.constants import DAYS, SHIFTS
from app.scheduler.person import Person
from app.scheduler.shift import Shift, VALID_DAYS, VALID_SHIFT_TIMES
from app.scheduler.shift_group import ShiftGroup
from typing import List

def parse_people_data(df: pd.DataFrame, shift_group: ShiftGroup, max_weekend: int = 1) -> List[Person]:
    """Parse people data from sheet and return list of Person objects.
       If max_weekend is provided, it overrides each Person's maximum weekend shifts.
    """
    # Fix the boolean columns
    boolean_columns = ["Double Shifts?", "3 Shift Days?", "Night + Noon"]
    for col in boolean_columns:
        df[col] = df[col].astype(str).str.strip().str.upper() == "TRUE"

    # Create uppercase version of column names for case-insensitive matching
    column_map = {col.upper(): col for col in df.columns}

    people = []
    for _, row in df.iterrows():
        name = row["Name"]
        unavailable = []
        
        # Get availability from column names
        for day in VALID_DAYS:
            for time in VALID_SHIFT_TIMES:
                column_key = f"{day} {time}".upper()
                if column_key in column_map:
                    original_col = column_map[column_key]
                    value = str(row[original_col]).strip().upper()
                    if value == "FALSE":
                        unavailable.append(shift_group.get_shift(day, time))

        # Create Person object
        person = Person(
            name=row["Name"],
            unavailable=unavailable,  # Will be converted to Shift objects later
            double_shift=row["Double Shifts?"],
            max_shifts=int(row["Max Shifts"]),
            max_nights=int(row["Max Nights"]),
            are_three_shifts_possible=row["3 Shift Days?"],
            night_and_noon_possible=row["Night + Noon"],
            shift_counts=0,
            night_counts=0,
            max_weekend_shifts=max_weekend
        )
        people.append(person)
    
    return people

def parse_shift_needs(df: pd.DataFrame, shift_group: ShiftGroup) -> List[Shift]:
    """Parse shift requirements and return list of (day, time, needed) tuples"""
    shifts_data = []
    
    for _, row in df.iterrows():
        day = row[df.columns[0]]  # First column is the day
        for shift_time in SHIFTS:
            if pd.notnull(row[shift_time]) and row[shift_time] > 0:
                shifts_data.append((day, shift_time, int(row[shift_time])))
    
    shifts = []
    for day, time, needed in shifts_data:
        shift = Shift(day, time, group=shift_group, needed=needed)
        shifts.append(shift)
    
    return shifts

def get_fresh_data(
    shift_needs_sheet_name: str = "Needed Shifts",
    people_sheet_name: str = "Real Data - 15/01",
    max_weekend: int = 1
) -> ShiftGroup:
    """
    Gets fresh data from Google Sheets and processes it into a ShiftGroup.
    If max_weekend is provided, it is used as the default for all Person objects.
    """
    # Get raw data from sheets
    shift_needs_raw = get_google_sheet_data("Shifts", shift_needs_sheet_name)
    people_raw = get_google_sheet_data("Shifts", people_sheet_name)
    
    # Create new ShiftGroup
    shift_group = ShiftGroup()
    
    # Parse and add shifts
    shift_group.shifts = parse_shift_needs(shift_needs_raw, shift_group)

    
    # Parse and add people
    people = parse_people_data(people_raw, shift_group, max_weekend=max_weekend)
    shift_group.people = people
    
    return shift_group

# print(shift_requirements)
# print(structured_data)