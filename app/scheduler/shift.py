from typing import Literal, get_args, Optional, List

# Define the allowed types using Python's Literal type
DayType = Literal["Last Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ShiftTimeType = Literal["Morning", "Noon", "Evening", "Night"]

# Get the allowed values from the Literal types
VALID_DAYS = get_args(DayType)
VALID_SHIFT_TIMES = get_args(ShiftTimeType)

class Shift:
    # Initialize empty class variables
    ALL_SHIFTS: List['Shift'] = []
    WEEKEND_SHIFTS: List['Shift'] = []
    WEEKDAY_SHIFTS: List['Shift'] = []

    def __init__(self, shift_day: DayType, shift_time: ShiftTimeType):
        # Validate using the values from Literal types
        if shift_day not in VALID_DAYS:
            raise ValueError(
                f"Invalid day: '{shift_day}'. Valid days are: {', '.join(VALID_DAYS)}"
            )
        
        if shift_time not in VALID_SHIFT_TIMES:
            raise ValueError(
                f"Invalid shift time: '{shift_time}'. Valid shift times are: {', '.join(VALID_SHIFT_TIMES)}"
            )
            
        self.shift_day = shift_day
        self.shift_time = shift_time

    # Class method to create all possible shifts
    @classmethod
    def create_all_shifts(cls) -> List['Shift']:
        return [cls(day, time) for day in VALID_DAYS for time in VALID_SHIFT_TIMES]

    # Class method to create weekend shifts
    @classmethod
    def create_weekend_shifts(cls) -> List['Shift']:
        return [shift for shift in cls.create_all_shifts() 
                if shift.is_weekend_shift]

    # Class method to create weekday shifts
    @classmethod
    def create_weekday_shifts(cls) -> List['Shift']:
        return [shift for shift in cls.create_all_shifts() 
                if not shift.is_weekend_shift]

    @property
    def previous_day(self) -> Optional[str]:
        """Get the previous day in the week sequence"""
        day_index = VALID_DAYS.index(self.shift_day)
        return VALID_DAYS[day_index - 1] if day_index > 0 else None

    @property
    def next_day(self) -> Optional[str]:
        """Get the next day in the week sequence"""
        day_index = VALID_DAYS.index(self.shift_day)
        return VALID_DAYS[day_index + 1] if day_index < len(VALID_DAYS) - 1 else None

    @property
    def previous_shift(self) -> Optional[str]:
        """Get the previous shift in the day sequence"""
        shift_index = VALID_SHIFT_TIMES.index(self.shift_time)
        return VALID_SHIFT_TIMES[shift_index - 1] if shift_index > 0 else None

    @property
    def next_shift(self) -> Optional[str]:
        """Get the next shift in the day sequence"""
        shift_index = VALID_SHIFT_TIMES.index(self.shift_time)
        return VALID_SHIFT_TIMES[shift_index + 1] if shift_index < len(VALID_SHIFT_TIMES) - 1 else None

    @property
    def is_weekend_shift(self) -> bool:
        """Determines if this is a weekend shift
        Weekend shifts are:
        - Friday Evening and Night shifts
        - All Saturday shifts
        """
        return (self.shift_day == "Friday" and self.shift_time in ["Evening", "Night"]) or \
               (self.shift_day == "Saturday")

    def __eq__(self, other: 'Shift') -> bool:
        """Defines how two shifts are compared for equality
        Two shifts are equal if they have the same day and time"""
        if not isinstance(other, Shift):
            return NotImplemented
        return (self.shift_day == other.shift_day and 
                self.shift_time == other.shift_time)

    def __hash__(self) -> int:
        """Makes Shift objects hashable (needed for sets)
        Two shifts that are equal will have the same hash"""
        return hash((self.shift_day, self.shift_time))

    def __str__(self) -> str:
        """Defines how a shift is converted to string
        Format: "DayName ShiftTime" (e.g., "Monday Morning")"""
        return f"{self.shift_day} {self.shift_time}"

    def __lt__(self, other: 'Shift') -> bool:
        """Defines how shifts are ordered (less than comparison)
        Orders shifts chronologically through the week"""
        
        # First compare days using their position in VALID_DAYS
        day_index_self = VALID_DAYS.index(self.shift_day)
        day_index_other = VALID_DAYS.index(other.shift_day)
        
        if day_index_self != day_index_other:
            return day_index_self < day_index_other
        
        # If same day, compare shift times using their position in VALID_SHIFT_TIMES
        return VALID_SHIFT_TIMES.index(self.shift_time) < VALID_SHIFT_TIMES.index(other.shift_time)

# Initialize the class variables after the complete class definition
Shift.ALL_SHIFTS = Shift.create_all_shifts()
Shift.WEEKEND_SHIFTS = Shift.create_weekend_shifts()
Shift.WEEKDAY_SHIFTS = Shift.create_weekday_shifts() 