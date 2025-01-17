from app.scheduler.constants import DAYS, SHIFTS

def get_adjacent_days(day):
    """Get the previous and next days for a given day."""
    day_index = DAYS.index(day)
    previous_day = DAYS[day_index - 1] if day_index > 0 else None
    next_day = DAYS[day_index + 1] if day_index < len(DAYS) - 1 else None
    return previous_day, next_day

def get_adjacent_shifts(shift):
    """Get the previous and next shifts for a given shift."""
    shift_index = SHIFTS.index(shift)
    previous_shift = SHIFTS[shift_index - 1] if shift_index > 0 else None
    next_shift = SHIFTS[shift_index + 1] if shift_index < len(SHIFTS) - 1 else None
    return previous_shift, next_shift

def debug_log(message, debug_mode = True):
    if debug_mode:
        print(message) 