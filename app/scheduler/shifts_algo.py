import os
import sys
from typing import List, Tuple

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
from itertools import combinations
import copy
from app.scheduler.person import Person
from app.scheduler.utils import debug_log
from app.scheduler.constants import DAYS, SHIFTS
from app.google_sheets.import_sheet_data import (
    get_fresh_data, 
    create_shift_group_from_requirements, 
    parse_shift_constraints
)
from app.scheduler.shift import Shift, VALID_DAYS
from app.scheduler.shift_group import ShiftGroup
from app.scheduler.combo_manager import ComboManager

debug_mode = True
def debug_log(message):
    if debug_mode:
        print(message)


def rank_shifts(shift_group: ShiftGroup, people: List[Person]) -> List[Shift]:
    """
    Rank shifts by their constraint level: available people / needed.
    Returns a sorted list of shifts, with most constrained first.
    """
    rankings = []
    for shift in shift_group.shifts:
        if shift.is_staffed:  # Skip already staffed shifts
            continue
            
        # Get eligible people for this shift
        eligible_people = [p for p in people if p.is_eligible_for_shift(shift)]
        
        if eligible_people:
            constraint_score = len(eligible_people) / shift.needed
        else:
            constraint_score = 0
            
        rankings.append((constraint_score, shift))
        print(f"Shift: {shift}, Needed: {shift.needed}, "
              f"Available people: {len(eligible_people)}, Score: {constraint_score}")

    sorted_rankings = sorted(rankings, key=lambda x: x[0])  # Sort by constraint score

    print("\n=== Ranked Shifts ===")
    for rank, (score, shift) in enumerate(sorted_rankings, 1):
        print(f"Rank {rank}: {shift} with score {score}")
    print("=====================\n")
    
    # Return just the sorted shifts
    return [shift for _, shift in sorted_rankings]


def validate_remaining_shifts(remaining_shifts, people):
    """Validate remaining shifts have enough eligible people"""
    for shift in remaining_shifts:
        eligible_people = [p for p in people if p.is_eligible_for_shift(shift)]
        if len(eligible_people) < shift.needed:
            print(f"Validation failed: {shift.shift_day} {shift.shift_time} needs {shift.needed} people, "
                    f"but only {len(eligible_people)} are available.")
            return False
    print("Validation passed: All shifts have enough eligible people.")
    return True

def get_previous_day(days, day):
    index = days.index(day)
    return days[index - 1] if index > 0 else None


def calculate_person_constraint(person, remaining_shifts, current_assignments):
    """Calculate constraint score for a person"""
    return person.calculate_constraint_score(remaining_shifts, current_assignments)
    

def backtrack_assign(remaining_shifts: List[Shift], people: List[Person], shift_group: ShiftGroup,
                    max_depth: int = 10000, depth: int = 0, 
                    cancel_event: threading.Event = None) -> Tuple[bool, str]:
    """
    Assign people to shifts using backtracking to ensure all constraints are satisfied.
    Returns: (bool, str) - (success, reason for failure if any)
    """
    # Check for cancellation at the start of each recursive call
    if cancel_event and cancel_event.is_set():
        return False, "Algorithm cancelled"

    if not remaining_shifts:
        return True, "success"

    # Create copies of shifts for this branch
    original_shifts = [shift.copy_with_group() for shift in remaining_shifts]
    
    current_shift = remaining_shifts[0]
    debug_log(f"\nDepth {depth}: Trying to assign {current_shift}")
    
    # Get eligible people for this shift
    eligible_people = [p for p in people if p.is_eligible_for_shift(current_shift)]
    print(f"\n=== {current_shift}: Trying to assign {current_shift.needed} people ===")
    print(f"Eligible people: {[p.name for p in eligible_people]}")

    # If not enough people are available, backtrack
    if len(eligible_people) < current_shift.needed:
        debug_log(f"BACKTRACK: Not enough eligible people ({len(eligible_people)} < {current_shift.needed})")
        return False, f"Not enough eligible people for {current_shift}"

    # Generate all combinations
    all_combos = [list(combo) for combo in combinations(eligible_people, current_shift.needed)]
    debug_log(f"Generated {len(all_combos)} combinations")

    # Compute constraint scores for each eligible person
    for person in eligible_people:
        person.calculate_constraint_score(current_shift.group)

    # Get initial sort by constraints from ComboManager
    combo_manager = ComboManager()
    constraint_sorted_combos = combo_manager.sort_combinations(all_combos, current_shift)
    
    # Convert to scored format for additional sorting
    scored_combos = [(sum(p.constraints_score for p in combo), combo) for combo in constraint_sorted_combos]
    
    # Count double shift opportunities in each combo
    def count_double_shifts(combo, shift, shift_group):
        return sum(1 for person in combo 
                  if person.double_shift and shift_group.is_consecutive_shift(person, shift))

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
        names_in_combo = {p.name for p in combo}
        return any(len(names_in_combo & target_pair) == 2 for target_pair in target_names_list)

    # Apply additional sorting criteria while maintaining relative constraint order
    final_sorted_combos = sorted(
        scored_combos,
        key=lambda x: (
            -int(has_both_target_names(x[1], target_names)),  # Target names first (1 or 0)
            -count_double_shifts(x[1], current_shift, shift_group),  # Then double shifts
            x[0]  # Finally, maintain constraint score order
        )
    )

    # Extract just the combinations without scores
    sorted_combos = [combo for _, combo in final_sorted_combos]

    tested_combos = []
    remaining_combos = [[p.name for p in combo] for combo in sorted_combos]
    # Try all combinations of eligible people for this shift
    for combo in sorted_combos:
        debug_log(f"================================================")
        debug_log(f"{len(remaining_combos)} Remaining combos: {remaining_combos}")
        debug_log(f"{len(tested_combos)} Tested combos: {tested_combos}")
        debug_log(f"Trying combination: {[p.name for p in combo]} for {current_shift}")
        debug_log(f"================================================")

        tested_combos.append([p.name for p in combo])
        remaining_combos.remove([p.name for p in combo])
        
        # Make the assignment
        for p in combo:
            p.assign_to_shift(current_shift)
            
        remaining_shifts.pop(0)
        current_shift.is_staffed = True
        debug_log(f"Removing {current_shift} from remaining shifts")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        
        ranked_shifts = [shift.copy_with_group() for shift in rank_shifts(shift_group, people)]
        
        if validate_remaining_shifts(ranked_shifts, people):
            result, reason = backtrack_assign(
                ranked_shifts, people, shift_group, max_depth=max_depth, depth=depth + 1, cancel_event=cancel_event
            )
            
            if result:
                return True, "success"
            
            # Undo the assignment before returning False
            else:
                for person in combo:
                    person.unassign_from_shift(current_shift)
                    current_shift.is_staffed = False
                remaining_shifts = [shift.copy_with_group() for shift in original_shifts]
            
        else:
            debug_log(f"Next iteration check failed: Undoing assignment for {current_shift}")

            # Undo the assignment (backtrack)
            for person in combo:
                person.unassign_from_shift(current_shift)
                current_shift.is_staffed = False

            remaining_shifts = [shift.copy_with_group() for shift in original_shifts]
            current_shift = remaining_shifts[0]

        debug_log(f"State after undoing {current_shift}:")
        debug_log(f"  Remaining shifts: {remaining_shifts}")
        debug_log(f"  People's shift counts: {[(p.name, p.shift_counts) for p in people]}")
        debug_log(f"  People's night counts: {[(p.name, p.night_counts) for p in people]}")
        
    debug_log(f"No valid combination found for {current_shift}. Backtracking...")
    debug_log("=============================================================================")
    debug_log(f"Undoing assignment for {current_shift}: {[p.name for p in combo]}")
    debug_log(f"Current depth: {depth}")
    debug_log("=============================================================================")
    debug_log(f"Remaining shifts after all combinations of {current_shift} failed: {remaining_shifts}")
    return False, "no_valid_combination"




def run_shift_algorithm(shift_group=None, people=None, timeout=None):
    """
    Run the algorithm with timeout
    
    Args:
        shift_group: ShiftGroup object containing all shifts
        people: List of Person objects
        timeout: Maximum time to run algorithm
        
    Returns:
        Tuple of (success, assignments, reason, shift_counts, people)
    """
    cancel_event = threading.Event()
    
    def algorithm_worker(shift_group, people):
        # If no data passed, get fresh data from import_sheet_data
        if shift_group is None or people is None:
            # Keep the same order as our return value
            shift_group, people = get_fresh_data()
        
        # Sort shifts based on constraint level
        remaining_shifts = rank_shifts(shift_group, people)
        
        # Run the backtracking assignment
        max_depth = 10000
        success, reason = backtrack_assign(
            remaining_shifts, 
            people,
            shift_group,
            max_depth=max_depth,
            cancel_event=cancel_event
        )
        
        # Keep consistent return order throughout the function
        return success, reason, shift_group, people

    with ThreadPoolExecutor() as executor:
        future = executor.submit(algorithm_worker, shift_group, people)
        try:
            success, reason, shift_group, people = future.result(timeout=timeout)
            
            if success:
                # Create web interface dictionaries
                assignments = {}
                for day in VALID_DAYS:
                    assignments[day] = {}
                    today_shifts = shift_group.get_all_shifts_from_day(day)
                    for shift in today_shifts:
                        if shift.is_staffed:
                            assignments[day][shift.shift_time] = [p.name for p in shift.assigned_people]
                        else:
                            assignments[day][shift.shift_time] = []
                
                # Create shift_counts dictionary from people
                shift_counts = {person.name: person.shift_counts for person in people}
                
                return success, assignments, reason, shift_counts, people
            else:
                return False, None, reason, None, None
            
        except TimeoutError:
            cancel_event.set()  # Signal algorithm to stop
            return False, None, "Algorithm timed out", None, None


if __name__ == '__main__':
    success, assignments, reason, shift_counts, people = run_shift_algorithm()
    
    if success:
        print("\n=== Shifts Successfully Assigned ===")
        for day, day_assignments in assignments.items():
            print(f"{day}")
            for shift_time, assigned_people in day_assignments.items():
                if assigned_people:
                    print(f"  {shift_time}: {', '.join(assigned_people)}")
                else:
                    print(f"  {shift_time}: Unassigned")
        
        print("\n=== Shifts Assigned Per Person ===")
        for person_name, count in shift_counts.items():
            print(f"{person_name}: {count} shifts")
            
    else:
        print(f"\nNo solution found: {reason}")