import os
import sys
import time
from typing import List, Tuple

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
from itertools import combinations
from app.scheduler.person import Person
from app.scheduler.utils import debug_log
from app.scheduler.constants import DAYS, SHIFTS
from app.google_sheets.import_sheet_data import (
    get_fresh_data
)
from app.scheduler.shift import Shift, VALID_DAYS
from app.scheduler.shift_group import ShiftGroup
from app.scheduler.combo_manager import ComboManager

debug_mode = True
def debug_log(message):
    if debug_mode:
        print(message)


def validate_eligibility_for_remaining_shifts(remaining_shifts, shift_group):
    shift_types = shift_group.get_remaining_shift_types()
    for shift_type in shift_types:
        needed_capacity = sum(shift.needed for shift in remaining_shifts if shift.shift_type == shift_type)
        eligible_capacity = shift_group.get_eligible_capacity_by_type(shift_type)
        if eligible_capacity < needed_capacity:
            print(f"Validation failed: {shift_type} needs {needed_capacity} people, "
                    f"but only {eligible_capacity} are available.")
            return False
    print("Validation passed: All shifts have enough eligible people.")
    return True

def backtrack_assign(remaining_shifts: List[Shift], shift_group: ShiftGroup,
                    max_depth: int = 10000, depth: int = 0, 
                    cancel_event: threading.Event = None,
                    combinations_checked: list = None) -> Tuple[bool, str]:
    """
    Assign people to shifts using backtracking to ensure all constraints are satisfied.
    Returns: (bool, str) - (success, reason for failure if any)
    """
    # Initialize combinations counter if this is the first call
    if combinations_checked is None:
        combinations_checked = [0]

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
    eligible_people = [p for p in shift_group.people if p.is_eligible_for_shift(current_shift)]
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

    # Get sorted combinations from ComboManager
    combo_manager = ComboManager()
    sorted_combos = combo_manager.sort_combinations(all_combos, current_shift, shift_group)

    tested_combos = []
    remaining_combos = [[p.name for p in combo] for combo in sorted_combos]
    
    # Introduce a flag to check if any solution was found at this depth
    is_any_valid = False

    # Try all combinations of eligible people for this shift
    for combo in sorted_combos:
        # Increment the combinations counter
        combinations_checked[0] += 1
        
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
        
        ranked_shifts = [shift.copy_with_group() for shift in shift_group.rank_shifts(shift_group.people)]
        
        if validate_eligibility_for_remaining_shifts(ranked_shifts, shift_group):
            result, reason = backtrack_assign(
                ranked_shifts, shift_group, max_depth=max_depth, 
                depth=depth + 1, cancel_event=cancel_event,
                combinations_checked=combinations_checked
            )
            
            if result:
                is_any_valid = True
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
        debug_log(f"  People's shift counts: {[(p.name, p.shift_counts) for p in shift_group.people]}")
        debug_log(f"  People's night counts: {[(p.name, p.night_counts) for p in shift_group.people]}")
        
    # If no valid combination was found for the current shift
    if not is_any_valid:
        debug_log(f"No valid combination found for {current_shift}. Backtracking...")
        debug_log("=============================================================================")
        
        # NEW: If this is the top-level shift, stop immediately instead of trying the next shift
        if depth == 0:
            debug_log("No valid combination for the top-level shift - returning immediately.")
            return False, "no_valid_combination_for_first_shift"

        debug_log(f"Undoing assignment for {current_shift}: {[p.name for p in combo]}")
        debug_log(f"Current depth: {depth}")
        debug_log("=============================================================================")
        debug_log(f"Remaining shifts after all combinations of {current_shift} failed: {remaining_shifts}")
        return False, "no_valid_combination"




def run_shift_algorithm(shift_group=None, timeout=None):
    """
    Run the algorithm with timeout
    
    Args:
        shift_group: ShiftGroup object containing all shifts
        people: List of Person objects
        timeout: Maximum time to run algorithm
        
    Returns:
        Tuple of (success, assignments, reason, shift_counts, people)
    """
    # Add timing at the start
    start_time = time.time()
    
    cancel_event = threading.Event()
    
    def algorithm_worker(shift_group):
        # If no data passed, get fresh data from import_sheet_data
        if shift_group is None:
            # Keep the same order as our return value
            shift_group = get_fresh_data()
        
        # Sort shifts based on constraint level
        remaining_shifts = shift_group.rank_shifts(shift_group.people)
        
        # Initialize combinations counter
        combinations_checked = [0]
        
        # Run the backtracking assignment
        max_depth = 10000
        success, reason = backtrack_assign(
            remaining_shifts, 
            shift_group,
            max_depth=max_depth,
            cancel_event=cancel_event,
            combinations_checked=combinations_checked
        )
        
        # Keep consistent return order throughout the function
        return success, reason, shift_group, combinations_checked[0]

    with ThreadPoolExecutor() as executor:
        future = executor.submit(algorithm_worker, shift_group)
        try:
            success, reason, shift_group, total_combinations = future.result(timeout=timeout)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            print(f"\nScheduling algorithm completed in {execution_time:.2f} seconds")
            print(f"Total combinations checked: {total_combinations}")
            
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
                shift_counts = {person.name: person.shift_counts for person in shift_group.people}
                
                return success, assignments, reason, shift_counts, shift_group.people
            else:
                return False, None, reason, None, None
            
        except TimeoutError:
            execution_time = time.time() - start_time
            print(f"\nAlgorithm timed out after {execution_time:.2f} seconds")
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