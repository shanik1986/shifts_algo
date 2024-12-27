
def debug_log_assignment_attempt(day, shift, needed, people, remaining_shifts):
    """
    Log the state before attempting to assign people to a shift.
    """
    print(f"\n--- Attempting to assign {needed} people for {day} {shift} ---")

    # Log people and their current limitations
    print("State before assignment:\nPeople\n=====")
    for person in people:
        print(f"Name: {person['name']}, Assigned Nights: {person.get('assigned_nights', 0)}, \              Max Nights: {person['max_nights']}, Assigned Shifts: {person.get('assigned_shifts', 0)}, \              Max Shifts: {person['max_shifts']}")

    # Log remaining shifts
    print("\nRemaining Shifts before assignment:\n========================")
    for day_name, shifts in remaining_shifts.items():
        for shift_name, needed_count in shifts.items():
            print(f"{day_name} {shift_name}: {needed_count} needed")


def debug_log_eligible_people(day, shift, eligible_people):
    """
    Log the eligible people for a specific shift.
    """
    print(f"\nEligible People for {day} {shift}:")
    print("===================")
    for person in eligible_people:
        print(f"Name: {person['name']}, Nights: {person.get('assigned_nights', 0)}/{person['max_nights']}, \              Shifts: {person.get('assigned_shifts', 0)}/{person['max_shifts']}")


def debug_log_state_after_assignment(day, shift, remaining_shifts, current_assignments, shift_counts, night_counts):
    """
    Log the state after an assignment is made.
    """
    print(f"\nState after assigning {day} {shift}:")

    # Log remaining shifts
    print("Remaining Shifts:\n========================")
    for day_name, shifts in remaining_shifts.items():
        for shift_name, needed_count in shifts.items():
            print(f"{day_name} {shift_name}: {needed_count} needed")

    # Log current assignments
    print("\nCurrent Assignments:\n========================")
    for day_name, shifts in current_assignments.items():
        for shift_name, assigned_people in shifts.items():
            assigned_names = [person['name'] for person in assigned_people]
            print(f"{day_name} {shift_name}: {', '.join(assigned_names)}")

    # Log counts
    print("\nShift and Night Counts:\n========================")
    for name, count in shift_counts.items():
        print(f"{name}: Shifts Assigned: {count}, Nights Assigned: {night_counts[name]}")


def debug_log_backtrack(day, shift, remaining_shifts, current_assignments):
    """
    Log the state after backtracking.
    """
    print(f"\nBacktracking: Undoing assignment for {day} {shift}")

    # Log remaining shifts
    print("Remaining Shifts after backtracking:\n========================")
    for day_name, shifts in remaining_shifts.items():
        for shift_name, needed_count in shifts.items():
            print(f"{day_name} {shift_name}: {needed_count} needed")

    # Log current assignments
    print("\nCurrent Assignments after backtracking:\n========================")
    for day_name, shifts in current_assignments.items():
        for shift_name, assigned_people in shifts.items():
            assigned_names = [person['name'] for person in assigned_people]
            print(f"{day_name} {shift_name}: {', '.join(assigned_names)}")
