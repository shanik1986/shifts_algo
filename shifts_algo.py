from import_constraints import structured_data
from itertools import combinations
from validations import get_eligible_people
import sys

# Define constants for days and shifts
DAYS = [
    "Last Saturday", "Sunday", "Monday", "Tuesday", 
    "Wednesday", "Thursday", "Friday", "Saturday"
]
SHIFTS = ["Morning", "Noon", "Evening", "Night"]
# Define shifts per day
shifts_per_day = {
    
   "Last Saturday": {"Night": 1},
   "Sunday": {"Morning": 1, "Noon": 3, "Evening": 3, "Night": 1},
    "Monday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 0},
    "Tuesday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 1},
    "Wednesday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 2},
    "Thursday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
   "Friday": {"Morning": 3, "Noon": 3, "Evening": 3, "Night": 3},
    "Saturday": {"Morning": 3, "Noon": 3, "Evening": 3},
}

# Placeholder for people data (we will add more dynamically later)



# # # Test Data

# people = [
#      {"name": "Person1", "max_shifts": 10, "max_nights": 2, "unavailable": [], "double_shift": True},
#      {"name": "Person2", "max_shifts": 10, "max_nights": 2, "unavailable": [], "double_shift": True},
#      {"name": "Person3", "max_shifts": 10, "max_nights": 2, "unavailable": [], "double_shift": True},
#  ]

# shifts_per_day = {
#      "Sunday": {"Morning": 1, "Evening": 1, "Night": 1},
#      "Monday": {"Morning": 0, "Noon": 1, "Evening": 2, "Night": 1},
#      "Tuesday": {"Morning": 1, "Evening": 1, "Night": 2},
#      "Wednesday": {"Morning": 1, "Noon": 2},
#  }


debug_mode = True
def debug_log(message):
    if debug_mode:
        print(message)


def rank_shifts(remaining_shifts, shift_counts, people):
    """
    Rank shifts by their constraint level: available people / remaining needed.
    Log the ranking process for debugging.
    """
    rankings = []
    for i, (day, shift, needed) in enumerate(remaining_shifts):
        debug_log(f"[rank_shifts]")
        available_people = get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments, debug_mode=False)
        if available_people:
            constraint_score = len(available_people) / needed
        else:
            constraint_score = 0
        rankings.append((constraint_score, (day, shift, needed)))
        print(f"Shift: {day} {shift}, Needed: {needed}, "
                f"Available people: {len(available_people)}, Score: {constraint_score}")

    sorted_rankings_with_score = sorted(rankings, key=lambda x: x[0])

    print("\n=== Ranked Shifts ===")
    for rank, (score, (day, shift, needed)) in enumerate(sorted_rankings_with_score, 1):
        print(f"Rank {rank}: {day} {shift} with score {score}")
    print("=====================\n")
    sorted_rankings = [(day, shift, needed) for i, (score, (day, shift, needed)) in enumerate(sorted_rankings_with_score)]
    
    return sorted_rankings

# def validate_night_to_morning_constraint(current_assignments, day, shift, assigned_people):
#     """
#     Validates that no person assigned to the current shift violates the night-to-morning constraint.
#     """
#     day_index = DAYS.index(day)
#     if shift == "Morning":
#         if day_index == 0:
#             return True  # Skip validation for the first day (no previous day)

#         previous_day = DAYS[day_index - 1]
#         previous_night_people = [p["name"] for p in current_assignments[previous_day]["Night"]]
#         for person in assigned_people:
#             if person["name"] in previous_night_people:
#                 debug_log(f"Constraint Violated During Assignment: {person['name']} is assigned to both {previous_day} Night and {day} Morning!")
#                 return False
#         return True
#     elif shift == "Night":
#         if day_index == len(DAYS) - 1:
#             return True # Skip validation for the last day (no next day)
        
#         next_day = DAYS[day_index + 1]
#         next_morning_people = [p["name"] for p in current_assignments[next_day]["Morning"]]
#         for person in assigned_people:
#             if person["name"] in next_morning_people:
#                 debug_log(f"Constraint Violated During Assignment: {person['name']} is assigned to both {next_day} Morning and {day} Night!")
#                 return False
#         return True
def validate_remaining_shifts(remaining_shifts, people, shift_counts):
    """
    Validate that all remaining shifts have enough eligible people to fill them.
    """
    for i, (day, shift, needed) in enumerate(remaining_shifts):
        eligible_people = get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments, debug_mode=False)
        if len(eligible_people) < needed:
            print(f"Validation failed: {day} {shift} needs {needed} people, "
                    f"but only {len(eligible_people)} are available.")
            return False
    print("Validation passed: All shifts have enough eligible people.")
    return True

def get_previous_day(days, day):
    index = days.index(day)
    return days[index - 1] if index > 0 else None

def validate_final_constraints(current_assignments):
    """
    Validate that the final assignments respect all constraints, including night-to-morning.
    """
    for day, day_shifts in current_assignments.items():
        for shift, people in day_shifts.items():
            if shift == "Morning":
                previous_day = get_previous_day(DAYS, day)
                if previous_day:
                    night_people = [p["name"] for p in current_assignments[previous_day]["Night"]]
                    for person in people:
                        if person["name"] in night_people:
                            debug_log(f"Final validation failed: {person['name']} assigned to both {previous_day} Night and {day} Morning!")
                            return False
    return True


def calculate_person_constraint(person, remaining_shifts):
    """
    Calculate the constraint score for a person based on the number of shifts
    they are eligible for compared to their maximum shifts.
    """
    available_shifts = [
        (day, shift) for i, (day, shift, needed) in enumerate(remaining_shifts)
        if (day, shift) not in person["unavailable"]
    ]
    return len(available_shifts) / person["max_shifts"] if person["max_shifts"] > 0 else float("inf")
    

def backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments):
    import copy
    """
    Assign people to shifts using backtracking to ensure all constraints are satisfied.
    """
    # Base Case: Check if all shifts are processed (remaining_shifts are 0)

    # if  all(needed == 0 for day_shifts in remaining_shifts.values() for needed in day_shifts.values()):
    if not(remaining_shifts):
        debug_log("All shifts successfully assigned! Validating constraints...")
        return True
        # if validate_final_constraints(current_assignments):
            # debug_log("Final validation passed!")
            # return True
        # else:
            # debug_log("Final validation failed!")
            # return False
    
    original_shifts = copy.deepcopy(remaining_shifts)

    day, shift, needed = remaining_shifts[0]
    debug_log(f"\n--- Attempting to assign {needed} people to {day} {shift} ---")
    debug_log(f"Current state before assignment:")
    debug_log(f"  Remaining shifts: {remaining_shifts}")
    debug_log(f"  Shift counts: {shift_counts}")
    debug_log(f"  Night counts: {night_counts}")
    debug_log(f"  Current assignments: {current_assignments}")

    # Get eligible people for this shift
    eligible_people = get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments)
    debug_log(f"Eligible people for {day} {shift}: {[p['name'] for p in eligible_people]}")

    # If not enough people are available, backtrack
    if len(eligible_people) < needed:
        debug_log(f"Not enough eligible people for {day} {shift}. Backtracking...")
        return False

    if not(validate_remaining_shifts(remaining_shifts, people, shift_counts)):
        return False

    # Compute constraint scores for each eligible person
    person_scores = {p["name"]: calculate_person_constraint(p, remaining_shifts) for p in eligible_people}

    # Generate all combinations and calculate their constraint scores
    combo_scores = []
    for combo in combinations(eligible_people, needed):
        combo_score = sum(person_scores[p["name"]] for p in combo)  # Sum constraint scores of people in the combo
        combo_scores.append((combo_score, list(combo)))

    # Sort combinations by their total constraint score (lowest score first)
    combo_scores.sort(key=lambda x: x[0])

    # Try all combinations of eligible people for this shift
    for combo_score, combo in combo_scores:
        debug_log(f"Trying combination: {[p['name'] for p in combo]} for {day} {shift}")
        # # Validate night-to-morning constraint for morning and night shifts
        # if shift == "Morning" or shift == "Night":
        #     if not validate_night_to_morning_constraint(current_assignments, day, shift, combo):
        #         debug_log(f"Night-to-morning constraint violated for {day} {shift}. Undoing assignment...")
        #         continue  # Skip to the next combination




        # Make the assignment
        # current_assignments[day][shift] = list(combo)
        for p in combo:
            current_assignments[day][shift].append(p["name"])

        for person in combo:
            shift_counts[person["name"]] += 1
            if shift=="Night":
                night_counts[person["name"]] += 1
        # remaining_shifts[day][shift] -= needed
        debug_log(f"Removing {day} {shift} from remaining shifts")
        remaining_shifts.pop(0)
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        

        # Log the current state after assignment
        debug_log(f"State after assigning {day} {shift}:")
        debug_log(f"  Shift counts: {shift_counts}")
        debug_log(f"  Night counts: {night_counts}")
        debug_log(f"  Current assignments: {current_assignments}")
        # remaining_shifts = rank_shifts(remaining_shifts, shift_counts, people)
        
        
        # if not(validate_remaining_shifts(remaining_shifts, people, shift_counts)):
        #     return False
        # else:
        #     debug_log(f"Creating new recursive call for ")
        result = backtrack_assign(copy.deepcopy(rank_shifts(remaining_shifts, shift_counts, people)), people, shift_counts, night_counts, current_assignments)
        
        if result:
            return True
        
        debug_log(f"Recursive call for {day} {shift} returned: {result}")
        # Undo the assignment (backtrack)
        for person in combo:
            shift_counts[person["name"]] -= 1
            if shift=="Night":
                night_counts[person["name"]] -= 1
        current_assignments[day][shift] = []
        
        debug_log(f"Backtracking: Undoing assignment for {day} {shift}: {[p['name'] for p in combo]}")
        
        # remaining_shifts.insert(0, (day, shift, needed))
        
        debug_log(f"Remaining shifts: {remaining_shifts}")

        
        debug_log(f"Restoring {day} {shift} back on remaining shifts")
        remaining_shifts = copy.deepcopy(rank_shifts(original_shifts, shift_counts, people))
        day, shift, needed = remaining_shifts[0]
        debug_log(f"State after undoing {day} {shift}:")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        debug_log(f"  Shift counts: {shift_counts}")
        debug_log(f"  Night counts: {night_counts}")
        debug_log(f"  Current assignments: {current_assignments}")
        
        # remaining_shifts = rank_shifts(remaining_shifts, shift_counts, people)
    debug_log(f"No valid combination found for {day} {shift}. Backtracking...")
    debug_log(f"Remaining shifts after all combinations of {day} {shift} failed: {remaining_shifts}")
    return False


# Prepare initial variables
people = structured_data
print(people)
sys.exit("Stopping for debugging.")
remaining_shifts = []
for day, shifts in shifts_per_day.items():
    for shift, needed in shifts.items():
        if needed > 0:
            remaining_shifts.append((day, shift, needed))





# Prepare initial assignments and counts
current_assignments = {day: {shift: [] for shift in SHIFTS} for day in DAYS}
shift_counts = {p["name"]: 0 for p in people}
night_counts = {p["name"]: 0 for p in people}
# print (night_counts)


# Sort shifts based on constraint level
remaining_shifts = rank_shifts(remaining_shifts, shift_counts, people)





# Run the backtracking assignment
if backtrack_assign(remaining_shifts, people, shift_counts, night_counts, current_assignments):
    print("\n=== Shifts Successfully Assigned ===")
    for day, shifts in current_assignments.items():
        print(f"{day}:")
        for shift, assigned in shifts.items():
            if assigned:
                # assigned_names = [p["name"] for p in assigned]
                print(f"  {shift}: {', '.join(assigned)}")
            else:
                print(f"  {shift}: Unassigned")
            
    
    # # Final Constraint Validation: Check for any violations
    # print("\n=== Final Constraint Validation ===")
    # for day, shifts in current_assignments.items():
    #     if day != "Last Saturday":  # Skip first day since it has no previous day
    #         previous_day = DAYS[DAYS.index(day) - 1]
    #         for person in shifts["Morning"]:
    #             if person in current_assignments[previous_day]["Night"]:
    #                 print(f"Constraint Violated: {person['name']} is assigned to both {previous_day} Night and {day} Morning!")
    print("Validation complete.")
    
    # Final log: Shifts assigned per person
    print("\n=== Shifts Assigned Per Person ===")
    for person in people:
        print(f"{person['name']}: {shift_counts[person['name']]} shifts")
else:
    print("\nNo solution found: Backtracking failed.")