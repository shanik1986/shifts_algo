import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Now we can import from app
from itertools import combinations
from app.scheduler.validations import get_eligible_people, is_person_eligible_for_shift, is_shift_assigned, get_adjacent_shifts
from app.scheduler.constants import DAYS, SHIFTS
from flask import jsonify, g, has_request_context
from app.google_sheets.import_sheet_data import get_fresh_data
import copy

debug_mode = True
def debug_log(message):
    if debug_mode:
        print(message)


def rank_shifts(remaining_shifts, shift_counts, people, night_counts, current_assignments):
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


def validate_remaining_shifts(remaining_shifts, people, shift_counts, night_counts, current_assignments):
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


def calculate_person_constraint(person, remaining_shifts, shift_counts, night_counts, current_assignments):
    """
    Calculate the constraint score for a person based on the number of shifts
    they are actually eligible for compared to their remaining shift capacity.
    
    Returns:
        float: Score representing how constrained this person is. 
        Lower score = more constrained (fewer available shifts relative to remaining capacity)
    """
    # Calculate remaining shifts capacity for this person
    remaining_capacity = person["max_shifts"] - shift_counts[person["name"]]
    if remaining_capacity <= 0:
        return float("inf")  # Person has no remaining capacity
        
    # Count shifts the person is actually eligible for
    eligible_shift_count = 0
    for day, shift, needed in remaining_shifts:
        if is_person_eligible_for_shift(
            person, day, shift,
            shift_counts, night_counts, current_assignments
        ):
            eligible_shift_count += 1
            
    return eligible_shift_count / remaining_capacity if remaining_capacity > 0 else float("inf")
    

def would_create_double_shift(person, day, shift, current_assignments):
    """
    Check if assigning this person to this shift would create a double shift
    """
    previous_shift, next_shift = get_adjacent_shifts(shift)
    
    # Check if person is assigned to adjacent shifts
    is_previous_assigned = previous_shift and is_shift_assigned(person, day, previous_shift, current_assignments)
    is_next_assigned = next_shift and is_shift_assigned(person, day, next_shift, current_assignments)
    
    return is_previous_assigned or is_next_assigned

def backtrack_assign(remaining_shifts, people, shift_counts, night_counts, 
                    current_assignments, max_depth=10000, depth=0, 
                    should_continue=lambda: True, iteration_counter=0):
    """
    Assign people to shifts using backtracking to ensure all constraints are satisfied.
    Returns: (bool, str) - (success, reason for failure if any)
    """
    # Check for cancellation every 100 iterations
    if iteration_counter % 100 == 0 and not should_continue():
        return False, "Request cancelled"

    if not remaining_shifts:
        return True, "success"

    original_shifts = copy.deepcopy(remaining_shifts)
    day, shift, needed = remaining_shifts[0]
    debug_log(f"\nDepth {depth}: Trying to assign {day} {shift}")
    
    # Get eligible people for this shift
    eligible_people = get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments)
    print(f"\n=== {day} {shift}: Trying to assign {needed} people ===")
    print(f"Eligible people: {[p['name'] for p in eligible_people]}")

    # If not enough people are available, backtrack
    if len(eligible_people) < needed:
        debug_log(f"BACKTRACK: Not enough eligible people ({len(eligible_people)} < {needed})")
        return False, f"Not enough eligible people for {day} {shift}"

    # Generate all combinations
    all_combos = list(combinations(eligible_people, needed))
    debug_log(f"Generated {len(all_combos)} combinations")

    # Compute constraint scores for each eligible person
    person_scores = {
        p["name"]: calculate_person_constraint(
            p, 
            remaining_shifts, 
            shift_counts, 
            night_counts, 
            current_assignments
        ) for p in eligible_people
    }

    # Generate all combinations and calculate their scores
    combo_scores = []
    for combo in all_combos:
        # Calculate regular constraint score
        constraint_score = sum(person_scores[p["name"]] for p in combo)
        combo_scores.append((constraint_score, list(combo)))

    # Sort combinations by their constraint score (lowest score first)
    combo_scores.sort(key=lambda x: x[0])

    # Count double shift opportunities in each combo
    def count_double_shifts(combo, day, shift, current_assignments):
        return sum(1 for person in combo 
                  if person["double_shift"] and would_create_double_shift(person, day, shift, current_assignments))

    # A list of target name pairs to check for in combos and prioritize
    target_names = [
        {"Avishay", "Shani Keynan"},
        {"Shani Keynan", "Eliran Ron"},
        {"Shani Keynan", "Nir Ozery"},
        {"Shani Keynan", "Yoram"},
        {"Shani Keynan", "Maor"}
    ]

    
    # The function returns True if the tested combo has any of the target name pairs
    def has_both_target_names(combo, target_names_list):
        names_in_combo = {p["name"] for p in combo}
        return any(len(names_in_combo & target_pair) == 2 for target_pair in target_names_list)

    # Sort combinations with priority: both target names first, then double shifts, then constraint score
    combo_scores = sorted(combo_scores, 
                         key=lambda x: (
                             -int(has_both_target_names(x[1], target_names)),  # Both target names first (1 or 0)
                             -count_double_shifts(x[1], day, shift, current_assignments),  # Then double shifts
                             x[0]  # Then constraint score
                         ))

    tested_combos = []
    remaining_combos = [[p["name"] for p in combo] for _, combo in combo_scores]
    # Try all combinations of eligible people for this shift
    for combo_score, combo in combo_scores:
        debug_log(f"================================================")
        debug_log(f"{len(remaining_combos)} Remaining combos: {remaining_combos}")
        debug_log(f"{len(tested_combos)} Tested combos: {tested_combos}")
        debug_log(f"Trying combination: {[p['name'] for p in combo]} for {day} {shift}")
        debug_log(f"================================================")

        tested_combos.append([p["name"] for p in combo])
        remaining_combos.remove([p["name"] for p in combo])
        
        # Make the assignment
        # current_assignments[day][shift] = list(combo)
        for p in combo:
            current_assignments[day][shift].append(p["name"])
            shift_counts[p["name"]] += 1
            if shift == "Night":
                night_counts[p["name"]] += 1

        remaining_shifts.pop(0)
        debug_log(f"Removing {day} {shift} from remaining shifts")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        

        # Log the current state after assignment
        debug_log(f"\nState after assigning {day} {shift}:")
        debug_log(f"======================================\n")
        debug_log(f"  Shift counts: {shift_counts}\n")
        debug_log(f"  Night counts: {night_counts}\n")
        # debug_log(f"  Current assignments: {current_assignments}\n")
        # remaining_shifts = rank_shifts(remaining_shifts, shift_counts, people)

        #Checking that all the shifts have available people after the lastest assignment
        debug_log(f"\nValidating all shifts after assigning {current_assignments[day][shift]} for {day} {shift}:")
        debug_log(f"======================================================================")
        
        ranked_shifts = copy.deepcopy(rank_shifts(remaining_shifts, shift_counts, people, night_counts, current_assignments))
        if validate_remaining_shifts(ranked_shifts, people, shift_counts, night_counts, current_assignments):
            result, reason = backtrack_assign(
                ranked_shifts, people, shift_counts, night_counts, 
                current_assignments, max_depth=max_depth, depth=depth + 1,
                should_continue=should_continue,
                iteration_counter=iteration_counter  # Pass the counter
            )
            
            if result:
                return True, "success"
            
                # Undo the assignment before returning False
            else:
                for person in combo:
                    shift_counts[person["name"]] -= 1
                    if shift == "Night":
                        night_counts[person["name"]] -= 1
                current_assignments[day][shift] = []
                remaining_shifts = copy.deepcopy(original_shifts)
                # return False, f"Recursive call returned {result}"
            
            
        else:
            debug_log(f"Next iteration check failed: Undoing assignment for {day} {shift}: {[p['name'] for p in combo]}")

        # Undo the assignment (backtrack)
            for person in combo:
                shift_counts[person["name"]] -= 1
                if shift == "Night":
                    night_counts[person["name"]] -= 1
            current_assignments[day][shift] = []
            remaining_shifts = copy.deepcopy(original_shifts)
            day, shift, needed = remaining_shifts[0]

        
        

        debug_log(f"State after undoing {day} {shift}:")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        debug_log(f"  Shift counts: {shift_counts}")
        debug_log(f"  Night counts: {night_counts}")
        # debug_log(f"  Current assignments: {current_assignments}")
        
    debug_log(f"No valid combination found for {day} {shift}. Backtracking...")
    debug_log("=============================================================================")
    debug_log(f"Undoing assignment for {day} {shift}: {[p['name'] for p in combo]}")
    debug_log(f"Current depth: {depth}")
    debug_log("=============================================================================")
    debug_log(f"Remaining shifts after all combinations of {day} {shift} failed: {remaining_shifts}")
    return False, "no_valid_combination"


def get_hello_world():
    return "Hello World from shifts_algo.py!"

def run_shift_algorithm(shift_requirements=None, shift_constraints=None):
    """
    Run the algorithm with either passed data or fetch from Google Sheets
    """
    def should_continue():
        """Check if we should continue processing"""
        if has_request_context():
            return getattr(g, 'request_active', True)
        return True  # Continue if not in request context (e.g., running locally)

    # If no data passed, get fresh data from import_sheet_data
    if shift_requirements is None or shift_constraints is None:
        shift_constraints, shift_requirements = get_fresh_data()

    # Use the data (either passed or from sheets)
    people = shift_constraints
    remaining_shifts = []
    
    for day, shifts in shift_requirements.items():
        for shift, needed in shifts.items():
            if needed > 0:
                remaining_shifts.append((day, shift, needed))

    # Calculate maximum possible depth
    total_shifts = sum(needed for _, _, needed in remaining_shifts)
    print(f"Total shifts that need to be assigned: {total_shifts}")

    # Calculate max combinations for any shift
    max_combinations = 0
    for day, shift, needed in remaining_shifts:
        num_combinations = len(list(combinations(people, needed)))
        if num_combinations > max_combinations:
            max_combinations = num_combinations
            max_shift = (day, shift, needed)

    print(f"Maximum combinations ({max_combinations}) occurs for shift: {max_shift}")

    # Calculate theoretical maximum depth
    theoretical_max_depth = total_shifts * max_combinations
    print(f"Theoretical maximum depth: {theoretical_max_depth}")

    # Prepare initial assignments and counts
    current_assignments = {day: {shift: [] for shift in SHIFTS} for day in DAYS}
    shift_counts = {p["name"]: 0 for p in people}
    night_counts = {p["name"]: 0 for p in people}
    
    # Sort shifts based on constraint level
    remaining_shifts = rank_shifts(remaining_shifts, shift_counts, people, night_counts, current_assignments)
    
    # Run the backtracking assignment with cancellation check
    max_depth = 10000
    success, reason = backtrack_assign(
        remaining_shifts, 
        people, 
        shift_counts, 
        night_counts, 
        current_assignments, 
        max_depth=max_depth,
        should_continue=should_continue  # Pass the check function
    )
    
    return success, current_assignments, reason, shift_counts, people

# Move all execution code inside this block
if __name__ == '__main__':
    success, assignments, reason, shift_counts, people = run_shift_algorithm()
    
    if success:
        print("\n=== Shifts Successfully Assigned ===")
        for day, shifts in assignments.items():
            print(f"{day}:")
            for shift, assigned in shifts.items():
                if assigned:
                    print(f"  {shift}: {', '.join(assigned)}")
                else:
                    print(f"  {shift}: Unassigned")
        
        print("\n=== Shifts Assigned Per Person ===")
        for person in people:
            print(f"{person['name']}: {shift_counts[person['name']]} shifts")
            
    else:
        print(f"\nNo solution found: {reason}")