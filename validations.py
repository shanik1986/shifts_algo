
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
def debug_log(message, debug_mode = True):
    if debug_mode:
        print(message)

def is_shift_blocked(day, shift, unavailable_shifts):
    return (day,shift) in unavailable_shifts

def is_max_shifts_reached(person, shift_counts):
    return shift_counts[person['name']] >= person['max_shifts']

def is_shift_assigned(person, day, tested_shift, current_assignments):
    return person['name'] in current_assignments[day][tested_shift]



# def print_unavailable_reason(message):


def get_eligible_people(day, shift, people, shift_counts, night_counts, current_assignments, debug_mode = True):
    from shifts_algo import DAYS, SHIFTS
    """
    Returns a list of eligible people for a specific day and shift.
    Eligibility is based on:
      1) Availability (not unavailable for this shift)
      2) Max shift limit not exceeded
      3) Not working a night shift before a morning shift
    """
    debug_log(f"\nGetting available people for {day} {shift}", debug_mode)
    debug_log("================================================", debug_mode)

    eligible_people = []
    day_index = DAYS.index(day)
    previous_day = DAYS[day_index - 1] if day_index > 0 else False
    next_day = DAYS[day_index + 1] if day_index < len(DAYS) - 1 else False

    shift_index = SHIFTS.index(shift)
    previous_shift = SHIFTS[shift_index - 1] if shift_index > 0 else SHIFTS[(len(SHIFTS) - 1)]
    next_shift = SHIFTS[shift_index + 1] if shift_index < 3 else SHIFTS[0]

    for person in people:
        debug_log(f"\nChecking {person['name']}'s availability...", debug_mode)
        
        # Check if this specific shift is available for this person
        if is_shift_blocked(day,shift,person["unavailable"]):
            debug_log(f"{person['name']} not eligible: Shift is unavailable", debug_mode)
            continue
        
        # Check if max shifts for person reached
        if is_max_shifts_reached(person, shift_counts):
            debug_log(f"{person['name']} not eligible: Already reached his maximum shifts ({person['max_shifts']})", debug_mode)
            continue

        # Check if this is the third shift today and whether it's allowed for this person


        if shift == "Morning":
            if previous_day and is_shift_assigned(person, previous_day, "Night", current_assignments):
                # Check that no shift assigned last night (if not last Saturday)
                debug_log(f"{person['name']} not eligible: Already assigned {previous_day} night",debug_mode)
                continue

            if not(person['double_shift']) and person['name'] in current_assignments[day][next_shift]:
            #     Check if person allows consecutive shifts and whether it's assigned
                debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {next_shift}"), debug_mode
                continue
        
        elif shift == "Noon":
            if previous_day and is_shift_assigned(person, previous_day, "Night", current_assignments):
                # Check that no shift assigned last night (if not last Saturday)
                debug_log(f"{person['name']} not eligible: Already assigned {previous_day} night", debug_mode)
                continue    
            
            if not(person["double_shift"]) and (person['name'] in current_assignments[day][next_shift] or person['name'] in current_assignments[day][previous_shift]):
                # Check if person allows consecutive shifts and whether it's assigned
                debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {next_shift} or {previous_shift}", debug_mode)
                continue

        
        elif shift == "Evening":
            if is_shift_assigned(person, day, "Night", current_assignments):
                # Check that no night shift assigned today
                debug_log(f"{person['name']} not eligible: Already assigned {day} night", debug_mode)
                continue
            if not(person["double_shift"]) and person['name'] in current_assignments[day][previous_shift]:
                # Check if person allows consecutive shifts and whether it's assigned
                debug_log(f"{person['name']} not eligible: No double shifts allowed. Already assigned for {day} {previous_shift}", debug_mode)
                continue
            

        elif shift == "Night":
            if night_counts[person['name']] >= person['max_nights']:
                # Check if person reached max nights limit
                debug_log(f"\n{person['name']} not eligible: Max night limitation breached ({person['max_nights']})", debug_mode)
                continue
            
            if next_day and is_shift_assigned(person, next_day, "Morning", current_assignments):
                # Check that no shift assigned tomorrow morning (if not Saturday)
                debug_log(f"{person['name']} not eligible: Already assigned {next_day} morning", debug_mode)
                continue
            
            if next_day and is_shift_assigned(person, next_day, "Noon", current_assignments):
                # Check that no shift assigned tomorrow noon (if not Saturday)
                debug_log(f"{person['name']} not eligible: Already assigned {next_day} noon", debug_mode)
                continue
            if is_shift_assigned(person, day, "Evening", current_assignments):
                # Check that no shift assigned today evening
                debug_log(f"{person['name']} not eligible: Already assigned {day} Evening", debug_mode)
                continue
    
        # Add eligible person
        debug_log(f"{person['name']} is eligible for {day} {shift}", debug_mode)
        eligible_people.append(person)
    
    debug_log(f"\nEligible people for {day} {shift}: {[p['name'] for p in eligible_people]}")

    return eligible_people
            