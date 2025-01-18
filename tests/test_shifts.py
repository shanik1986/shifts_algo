import pytest
from app.scheduler.utils import is_weekend_shift
from app.scheduler.constants import WEEKEND_SHIFTS, DAYS, SHIFTS


def test_weekend_shift_detection():
    # Validate that the weekend shifts are detected correctly by using the WEEKEND_SHIFTS constant
    for day, shift in WEEKEND_SHIFTS:
        assert is_weekend_shift(day, shift) == True

    # Create a list of tuple for every shift and remove the weekend shifts by using the WEEKEND_SHIFTS constant
    all_shifts = [(day, shift) for day in DAYS for shift in SHIFTS]
    for day, shift in WEEKEND_SHIFTS:
        all_shifts.remove((day, shift))

    # Validate that non-weekend shifts are detected correctly
    for day, shift in all_shifts:
        assert is_weekend_shift(day, shift) == False


