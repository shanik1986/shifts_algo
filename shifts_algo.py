from import_constraints import structured_data
import sys

# Define constants for days and shifts
days = [
    "Last Saturday", "Sunday", "Monday", "Tuesday", 
    "Wednesday", "Thursday", "Friday", "Saturday"
]
shifts = ["Morning", "Noon", "Evening", "Night"]
# Define shifts per day
shifts_per_day = {
    
   "Last Saturday": {"Night": 4},
   "Sunday": {"Morning": 3, "Noon": 2, "Evening": 2, "Night": 4},
    "Monday": {"Morning": 3, "Noon": 2, "Evening": 2, "Night": 4},
    "Tuesday": {"Morning": 3, "Noon": 2, "Evening": 2, "Night": 4},
    "Wednesday": {"Morning": 2, "Noon": 2, "Evening": 2, "Night": 4},
    "Thursday": {"Morning": 2, "Noon": 2, "Evening": 2, "Night": 4},
   "Friday": {"Morning": 2, "Noon": 2, "Evening": 2, "Night": 4},
    "Saturday": {"Morning": 2, "Noon": 2, "Evening": 2},
}

# Placeholder for people data (we will add more dynamically later)



# # # Test Data

# people = [
#      {"name": "Person1", "max_shifts": 10, "max_nights": 10, "unavailable": []},
#      {"name": "Person2", "max_shifts": 10, "max_nights": 10, "unavailable": []},
#      {"name": "Person3", "max_shifts": 10, "max_nights": 10, "unavailable": []},
#  ]

# shifts_per_day = {
#      "Sunday": {"Morning": 1, "Evening": 1, "Night": 0},
#      "Monday": {"Morning": 0}
#  }


debug_mode = True
def debug_log(message):
    if debug_mode:
        print(message)

def rank_people(remaining_shifts, people):
    """
    Rank people by their constraint level: available shifts / remaining shifts.
    Log the ranking process for debugging.
    """
    rankings = []
    for person in people:
        available_shifts = [
            (day, shift) for day, shifts in remaining_shifts.items()
            for shift, needed in shifts.items()
            if needed > 0 and (day, shift) not in person["unavailable"]
        ]
        if available_shifts:
            constraint_score = len(available_shifts) / person["max_shifts"]
        else:
            constraint_score = float("inf")  # Max constraint if no available shifts
        rankings.append((constraint_score, person))
        debug_log(f"Person: {person['name']}, Available shifts: {len(available_shifts)}, "
              f"Max shifts: {person['max_shifts']}, Score: {constraint_score}")
    
    sorted_rankings = sorted(rankings, key=lambda x: x[0])
    debug_log("\n=== Ranked People ===")
    for rank, (score, person) in enumerate(sorted_rankings, 1):
        debug_log(f"Rank {rank}: {person['name']} with score {score}")
    debug_log("=====================\n")
    return sorted_rankings

def rank_shifts(remaining_shifts, shift_counts, people):
    """
    Rank shifts by their constraint level: available people / remaining needed.
    Log the ranking process for debugging.
    """
    rankings = []
    for day, shifts in remaining_shifts.items():
        for shift, needed in shifts.items():
            if needed > 0:
                available_people = get_available_people(day,shift,people, shift_counts, night_counts, current_assignments)
                if available_people:
                    constraint_score = len(available_people) / needed
                else:
                    constraint_score = 0  # Max constraint if no people
                rankings.append((constraint_score, (day, shift, needed)))
                debug_log(f"Shift: {day} {shift}, Needed: {needed}, "
                      f"Available people: {len(available_people)}, Score: {constraint_score}")
    
    sorted_rankings = sorted(rankings, key=lambda x: x[0])
    # sorted_rankings = rankings
    debug_log("\n=== Ranked Shifts ===")
    for rank, (score, (day, shift, needed)) in enumerate(sorted_rankings, 1):
        debug_log(f"Rank {rank}: {day} {shift} with score {score}")
    debug_log("=====================\n")
    return sorted_rankings

# def get_available_people(day, shift, people, shift_counts):
#     """
#     Returns a list of eligible people for a specific day and shift.
#     Eligibility is based on:
#       1) Availability (not unavailable for this shift)
#       2) Max shift limit not exceeded
#       3) Additional conditions (e.g., double shifts, night+morning, etc.)
#     """
#     eligible_people = [
#         p for p in people
#         if (day, shift) not in p["unavailable"]  # Check availability
#         and shift_counts[p["name"]] < p["max_shifts"]  # Check shift limits
#     ]
#     return eligible_people

def get_available_people(day, shift, people, shift_counts, night_counts, current_assignments):
    """
    Returns a list of eligible people for a specific day and shift.
    Eligibility is based on:
      1) Availability (not unavailable for this shift)
      2) Max shift limit not exceeded
      3) Not working a night shift before a morning shift
    """


    eligible_people = []
    day_index = days.index(day)
    previous_day = days[day_index - 1] if day_index > 0 else False

    for person in people:
        # Check availability
        if (day, shift) in person["unavailable"]:
            continue
        
        # Check max shift limit
        if shift_counts[person["name"]] >= person["max_shifts"]:
            continue

        # Check night shift limit
        
        if night_counts[person["name"]] >= person["max_nights"]:
            continue
        
        
        # Validate night-to-morning constraint
        if shift == "Morning" and previous_day:
            previous_night_assignments = current_assignments[previous_day]["Night"]
            debug_log(f"Checking night-to-morning constraint for {person['name']} on {day} {shift}: {previous_day} Night = {previous_night_assignments}")
            if person in previous_night_assignments:
                debug_log(f"{person['name']} excluded from {day} {shift} because of a night shift on {previous_day}")
                continue

        # Add eligible person
        eligible_people.append(person)
    debug_log(f"Eligible people for {day} {shift}: {[p['name'] for p in eligible_people]}")

    return eligible_people

def validate_night_to_morning_constraint(current_assignments, day, assigned_people):
    """
    Validates that no person assigned to the current shift violates the night-to-morning constraint.
    """
    day_index = days.index(day)
    if day_index == 0:
        return True  # Skip validation for the first day (no previous day)

    previous_day = days[day_index - 1]
    previous_night_people = [p["name"] for p in current_assignments[previous_day]["Night"]]
    for person in assigned_people:
        if person["name"] in previous_night_people:
            debug_log(f"Constraint Violated During Assignment: {person['name']} is assigned to both {previous_day} Night and {day} Morning!")
            return False
    return True

def validate_remaining_shifts(remaining_shifts, people, shift_counts):
    """
    Validate that all remaining shifts have enough eligible people to fill them.
    """
    for day, shifts in remaining_shifts.items():
        for shift, needed in shifts.items():
            if needed > 0:  # Only check shifts that still need people
                eligible_people = get_available_people(day,shift, people, shift_counts, night_counts, current_assignments)
                if len(eligible_people) < needed:
                    debug_log(f"Validation failed: {day} {shift} needs {needed} people, "
                          f"but only {len(eligible_people)} are available.")
                    return False
    debug_log("Validation passed: All shifts have enough eligible people.")
    return True

def get_previous_day(days, day):
    index = days.index(day)
    return days[index - 1] if index > 0 else None

def validate_final_constraints(current_assignments):
    """
    Validate that the final assignments respect all constraints, including night-to-morning.
    """
    for day, shifts in current_assignments.items():
        for shift, people in shifts.items():
            if shift == "Morning":
                previous_day = get_previous_day(days, day)
                if previous_day:
                    night_people = [p["name"] for p in current_assignments[previous_day]["Night"]]
                    for person in people:
                        if person["name"] in night_people:
                            debug_log(f"Final validation failed: {person['name']} assigned to both {previous_day} Night and {day} Morning!")
                            return False
    return True


def backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments, shift_order, index=0):
    """
    Assign people to shifts using backtracking to ensure all constraints are satisfied.
    """
    # Base Case: Check if all shifts are processed (remaining_shifts are 0)

    if  all(needed == 0 for day_shifts in remaining_shifts.values() for needed in day_shifts.values()):
        debug_log("All shifts successfully assigned! Validating constraints...")
        if validate_final_constraints(current_assignments):
            debug_log("Final validation passed!")
            return True
        else:
            debug_log("Final validation failed!")
            return False
    day, shift, needed = shift_order[index]
    debug_log(f"\n--- Attempting to assign {needed} people to {day} {shift} ---")
    debug_log(f"Current state before assignment:")
    debug_log(f"  Remaining shifts: {remaining_shifts}")
    debug_log(f"  Shift counts: {shift_counts}")
    debug_log(f"  Night counts: {night_counts}")
    debug_log(f"  Current assignments: {current_assignments}")

    # Skip shifts with zero needed assignments
    if needed == 0:
        return backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments, shift_order, index + 1)

    # Get eligible people for this shift
    eligible_people = get_available_people(day, shift, people, shift_counts, night_counts, current_assignments)

    # Sort eligible people based on their flexibility
    eligible_people.sort(key=lambda p: len([
    (day, shift) for day, shifts in remaining_shifts.items()
    for shift, needed in shifts.items() if needed > 0 and (day, shift) not in p["unavailable"]
]))

    debug_log(f"Eligible people for {day} {shift}: {[p['name'] for p in eligible_people]}")

    # If not enough people are available, backtrack
    if len(eligible_people) < needed:
        debug_log(f"Not enough eligible people for {day} {shift}. Backtracking...")
        return False

    # Try all combinations of eligible people for this shift
    from itertools import combinations
    for combo in combinations(eligible_people, needed):
        debug_log(f"Trying combination: {[p['name'] for p in combo]} for {day} {shift}")
        # Validate night-to-morning constraint only for morning shifts
        if shift == "Morning":
            if not validate_night_to_morning_constraint(current_assignments, day, combo):
                debug_log(f"Night-to-morning constraint violated for {day} {shift}. Undoing assignment...")
                # # Undo the assignment (backtrack)
                # for person in combo:
                #     shift_counts[person["name"]] -= 1
                # current_assignments[day][shift] = []
                # remaining_shifts[day][shift] += needed
                continue  # Skip to the next combination




        # Make the assignment
        current_assignments[day][shift] = list(combo)
        for person in combo:
            shift_counts[person["name"]] += 1
            if shift=="Night":
                night_counts[person["name"]] += 1
        remaining_shifts[day][shift] -= needed

        # Log the current state after assignment
        debug_log(f"State after assigning {day} {shift}:")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        debug_log(f"  Shift counts: {shift_counts}")
        debug_log(f"  Night counts: {night_counts}")
        debug_log(f"  Current assignments: {current_assignments}")



        result = backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments, shift_order, index + 1)
        debug_log(f"Recursive call for {day} {shift} returned: {result}")
        if result:
            return True

        # Undo the assignment (backtrack)
        debug_log(f"Backtracking: Undoing assignment for {day} {shift}: {[p['name'] for p in combo]}")
        for person in combo:
            shift_counts[person["name"]] -= 1
            if shift=="Night":
                night_counts[person["name"]] -= 1
        current_assignments[day][shift] = []
        remaining_shifts[day][shift] += needed

        debug_log(f"State after undoing {day} {shift}:")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        debug_log(f"  Shift counts: {shift_counts}")
        debug_log(f"  Night counts: {night_counts}")
        debug_log(f"  Current assignments: {current_assignments}")
        
    debug_log(f"No valid combination found for {day} {shift}. Backtracking...")
    return False


# Prepare initial variables
people = structured_data
remaining_shifts = shifts_per_day.copy()

# Prepare initial assignments and counts
current_assignments = {day: {shift: [] for shift in shifts} for day in days}
shift_counts = {p["name"]: 0 for p in people}
night_counts = {p["name"]: 0 for p in people}
# print (night_counts)
# sys.exit("Stopping program for debugging after initializing night_counts.")

# Sort shifts based on constraint level
sorted_shift_rankings = rank_shifts(remaining_shifts, shift_counts, people)
shift_order = [(day, shift, needed) for _, (day, shift, needed) in sorted_shift_rankings]



# Run the backtracking assignment
if backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments, shift_order):
    print("\n=== Shifts Successfully Assigned ===")
    for day, shifts in current_assignments.items():
        print(f"{day}:")
        for shift, assigned in shifts.items():
            if assigned:
                assigned_names = [p["name"] for p in assigned]
                print(f"  {shift}: {', '.join(assigned_names)}")
            else:
                print(f"  {shift}: Unassigned")
            
    
    # Final Constraint Validation: Check for any violations
    print("\n=== Final Constraint Validation ===")
    for day, shifts in current_assignments.items():
        if day != "Last Saturday":  # Skip first day since it has no previous day
            previous_day = days[days.index(day) - 1]
            for person in shifts["Morning"]:
                if person in current_assignments[previous_day]["Night"]:
                    print(f"Constraint Violated: {person['name']} is assigned to both {previous_day} Night and {day} Morning!")
    print("Validation complete.")
    
    # Final log: Shifts assigned per person
    print("\n=== Shifts Assigned Per Person ===")
    for person in people:
        print(f"{person['name']}: {shift_counts[person['name']]} shifts")
else:
    print("\nNo solution found: Backtracking failed.")



# debug_log(shift_order)


# debug_log(remaining_shifts)
# rank_people(people, remaining_shifts)
# rank_shifts(remaining_shifts, people)

# # Testing
# remaining_shifts = shifts_per_day_test.copy()

# # Validate remaining shifts
# is_valid = validate_remaining_shifts(shifts_per_day_test, people_test, shift_counts_test)

# if not is_valid:
#     debug_log("\nValidation failed as expected.")
# else:
#     debug_log("\nValidation passed unexpectedly!")
