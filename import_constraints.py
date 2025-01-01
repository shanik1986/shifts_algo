import pandas as pd

# Define days and shifts
days = ["Last Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
shifts = ["Morning", "Noon", "Evening", "Night"]

# Load the CSV file
file_path = "Shifts - Real Data - 01.01.csv"  # Replace with your actual file name
# file_path = "test_data.csv"  # Replace with your actual file name
df = pd.read_csv(file_path)

# Fix the "Double Shifts?" and "3 Shift Days?" columns to ensure proper booleans
df["Double Shifts?"] = df["Double Shifts?"].astype(str).str.strip().str.upper() == "TRUE"
df["3 Shift Days?"] = df["3 Shift Days?"].astype(str).str.strip().str.upper() == "TRUE"

# Parse the dataset into a structured format
def parse_shift_data(df):
    processed_data = []
    for _, row in df.iterrows():
        unavailable = []
        column_index = 8  # Start with "Last Saturday Night"

        # Loop through days and shifts
        for day in days:
            for shift in shifts:
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

# Process the dataset
structured_data = parse_shift_data(df)

# # Output the structured data for validation
# for person in structured_data:
#     print(f"Name: {person['name']}, Double Shift: {person['double_shift']}, "
#           f"Max Shifts: {person['max_shifts']}, Max Nights: {person['max_nightss']}, "
#           f"Unavailable: {person['unavailable']}")

# print(structured_data)