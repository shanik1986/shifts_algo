"""
Constraints:
1) Specific unavailable shifts
2) Max shifts per person
3) Max nights per person
4) Consecutive shifts specific people
5) 3 shifts a day for specific people
6) Noon after night constraint
7) Night after Evening constraint
8) Morning after night constraint


"""
from app.scheduler.constants import DAYS, SHIFTS

def debug_log(message, debug_mode = True):
    if debug_mode:
        print(message)

def is_shift_blocked(day, shift, unavailable_shifts):
    return (day,shift) in unavailable_shifts

def is_max_shifts_reached(person, shift_counts):
    return shift_counts[person['name']] >= person['max_shifts']

def is_shift_assigned(person, tested_day, tested_shift, current_assignments):
    return person['name'] in current_assignments[tested_day][tested_shift]

def is_third_shift(person, day, current_assignments):
    # debug_log(f"Checking if this is the third shift for {person}")
    counter = 0
    for assigned_people in current_assignments[day].values():
        if person['name'] in assigned_people:
            counter+=1
    return counter >=3




# def print_unavailable_reason(message):


def get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments, debug_mode = True):
    """
    Returns a list of eligible people for a specific day and shift.
    """
    debug_log(f"\nGetting available people for {day} {shift}", debug_mode)
    debug_log("================================================", debug_mode)

    eligible_people = []
    
    for person in people:
        debug_log(f"\nChecking {person['name']}'s availability...", debug_mode)
        
        if is_person_eligible_for_shift(person, day, shift, shift_counts, night_counts, current_assignments):
            debug_log(f"{person['name']} is eligible for {day} {shift}", debug_mode)
            eligible_people.append(person)
        # else:
        #     debug_log(f"{person['name']} not eligible for {day} {shift}", debug_mode)
    
    debug_log(f"\nEligible people for {day} {shift}: {[p['name'] for p in eligible_people]}")
    return eligible_people
            
def is_person_eligible_for_shift(person, day, shift, shift_counts, night_counts, current_assignments, debug_mode=True):
    """
    Check if a specific person is eligible for a given shift based on all constraints.
    Returns: bool indicating if person is eligible
    """
    previous_day, next_day = get_adjacent_days(day)
    previous_shift, next_shift = get_adjacent_shifts(shift)

    # Check basic constraints
    if is_shift_blocked(day, shift, person["unavailable"]):
        debug_log(f"{person['name']} not eligible: Shift is unavailable", debug_mode)
        return False
    
    if is_max_shifts_reached(person, shift_counts):
        debug_log(f"{person['name']} not eligible: Already reached their maximum shifts ({person['max_shifts']})", debug_mode)
        return False

    # Check for Noon after night constraint based on person's preference
    if shift == "Noon" and previous_day:
        if is_shift_assigned(person, previous_day, "Night", current_assignments):
            if not person["night_and_noon_possible"]:
                debug_log(f"{person['name']} not eligible: Cannot do Noon after Night shift and assigned {previous_day} night" , debug_mode)
                return False
            
    # Check for Night before Noon constraint based on person's preference
    elif shift == "Night" and next_day:
        if is_shift_assigned(person, next_day, "Noon", current_assignments):
            if not person["night_and_noon_possible"]:
                debug_log(f"{person['name']} not eligible: Cannot do Night before Noon shift and assigned {next_day} noon", debug_mode)
                return False

    if is_third_shift(person, day, current_assignments):
        if not person["are_three_shifts_possible"]:
            debug_log(f"{person['name']} not eligible: Third shift a day restriction", debug_mode)
            return False
        elif shift == "Evening" or is_shift_assigned(person, day, "Evening", current_assignments):
            debug_log(f"{person['name']} not eligible: Cannot do Evening shift as third shift", debug_mode)
            return False

    # Shift-specific constraints
    if shift == "Morning":
        if previous_day and is_shift_assigned(person, previous_day, "Night", current_assignments):
            debug_log(f"{person['name']} not eligible: Already assigned {previous_day} night", debug_mode)
            return False
        if not person['double_shift'] and is_shift_assigned(person, day, next_shift, current_assignments):
            debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {next_shift}", debug_mode)
            return False

    elif shift == "Noon":    
        if not person["double_shift"] and (
            is_shift_assigned(person, day, next_shift, current_assignments) or 
            is_shift_assigned(person, day, previous_shift, current_assignments)
        ):
            debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {next_shift} or {previous_shift}", debug_mode)
            return False

    elif shift == "Evening":
        if is_shift_assigned(person, day, "Night", current_assignments):
            debug_log(f"{person['name']} not eligible: Already assigned {day} night", debug_mode)
            return False
        if not person["double_shift"] and (
            is_shift_assigned(person, day, next_shift, current_assignments) or 
            is_shift_assigned(person, day, previous_shift, current_assignments)
        ):
            debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {previous_shift}", debug_mode)
            return False

    elif shift == "Night":
        if night_counts[person['name']] >= person['max_nights']:
            debug_log(f"{person['name']} not eligible: Max night limitation breached ({person['max_nights']})", debug_mode)
            return False
        if next_day and is_shift_assigned(person, next_day, "Morning", current_assignments):
            debug_log(f"{person['name']} not eligible: Already assigned {next_day} morning", debug_mode)
            return False
        if not person["double_shift"] and is_shift_assigned(person, day, previous_shift, current_assignments):
            debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {previous_shift}", debug_mode)
            return False
        if is_shift_assigned(person, day, "Evening", current_assignments):
            debug_log(f"{person['name']} not eligible: Already assigned {day} Evening", debug_mode)
            return False

    return True
            
def get_adjacent_shifts(shift):
    """
    Get the previous and next shifts for a given shift.
    Returns: (previous_shift, next_shift)
    """
    shift_index = SHIFTS.index(shift)
    previous_shift = SHIFTS[shift_index - 1] if shift_index > 0 else None
    next_shift = SHIFTS[shift_index + 1] if shift_index < len(SHIFTS) - 1 else None
    return previous_shift, next_shift

def get_adjacent_days(day):
    """
    Get the previous and next days for a given day.
    Returns: (previous_day, next_day)
    """
    day_index = DAYS.index(day)
    previous_day = DAYS[day_index - 1] if day_index > 0 else None
    next_day = DAYS[day_index + 1] if day_index < len(DAYS) - 1 else None
    return previous_day, next_day
            