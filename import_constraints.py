import pandas as pd
from init_sheet_access import get_google_sheet_data

# Parse the dataset into a structured format
def parse_shift_data(df):
    processed_data = []
    for _, row in df.iterrows():
        unavailable = []
        column_index = 8  # Start with "Last Saturday Night"

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
            "unavailable": unavailable
        }
        processed_data.append(person)
    
    return processed_data

# Define sheet parameters
sheet_name = "Shifts"
tab_name = "Real Data - 09/01"
df = get_google_sheet_data(sheet_name, tab_name)

# Define days and shifts
DAYS = ["Last Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SHIFTS = ["Morning", "Noon", "Evening", "Night"]

# Fix the "Double Shifts?" and "3 Shift Days?" columns to ensure proper booleans
df["Double Shifts?"] = df["Double Shifts?"].astype(str).str.strip().str.upper() == "TRUE"
df["3 Shift Days?"] = df["3 Shift Days?"].astype(str).str.strip().str.upper() == "TRUE"


# Process the dataset
structured_data = parse_shift_data(df)



# print(structured_data)