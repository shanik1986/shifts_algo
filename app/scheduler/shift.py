from typing import Literal, get_args, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.scheduler.person import Person  # Only import for type checking
    from app.scheduler.shift_group import ShiftGroup  # Move this inside TYPE_CHECKING

# Define the allowed types using Python's Literal type
DayType = Literal["Last Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ShiftTimeType = Literal["Morning", "Noon", "Evening", "Night"]
ShiftType = Literal["regular", "night", "weekend"]

# Get the allowed values from the Literal types
VALID_DAYS = get_args(DayType)
VALID_SHIFT_TIMES = get_args(ShiftTimeType)
VALID_SHIFT_TYPES = get_args(ShiftType)

class Shift:
    def __new__(cls, shift_day: DayType, shift_time: ShiftTimeType, group: 'ShiftGroup', needed: int = 0):
        # First check if shift exists in group
        existing_shift = group.get_shift(shift_day, shift_time)
        if existing_shift:
            return existing_shift  # Return existing instance

        return super().__new__(cls)

    def __init__(self, shift_day: DayType, shift_time: ShiftTimeType, group: 'ShiftGroup', needed: int = 0):
        # Only initialize if this is a new instance
        if not hasattr(self, 'shift_day'):  # Check if already initialized
            # Validate using the values from Literal types
            if shift_day not in VALID_DAYS:
                raise ValueError(
                    f"Invalid day: '{shift_day}'. Valid days are: {', '.join(VALID_DAYS)}"
                )
            
            if shift_time not in VALID_SHIFT_TIMES:
                raise ValueError(
                    f"Invalid shift time: '{shift_time}'. Valid shift times are: {', '.join(VALID_SHIFT_TIMES)}"
                )
            
            if not isinstance(needed, int) or needed < 0:
                raise ValueError(f"'needed' must be a non-negative integer, got {needed}")

            # Initialize new shift
            self.shift_day = shift_day
            self.shift_time = shift_time
            self.needed = needed
            self.assigned_people: List['Person'] = []
            self.group = group
            self.is_staffed = False
            # Add shift to group
            group.add_shift(self)

    # Class method to create all possible shifts
    @classmethod
    def create_all_shifts(cls, group: 'ShiftGroup') -> List['Shift']:
        return [cls(day, time, group=group, needed=0) 
                for day in VALID_DAYS 
                for time in VALID_SHIFT_TIMES]

    # Class method to create weekend shifts
    @classmethod
    def create_weekend_shifts(cls, group: 'ShiftGroup') -> List['Shift']:
        return [shift for shift in cls.create_all_shifts(group) 
                if shift.is_weekend_shift]

    # Class method to create weekday shifts
    @classmethod
    def create_weekday_shifts(cls, group: 'ShiftGroup') -> List['Shift']:
        return [shift for shift in cls.create_all_shifts(group) 
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

    @property
    def is_morning(self) -> bool:
        """Check if this is a morning shift"""
        return self.shift_time == "Morning"

    @property
    def is_noon(self) -> bool:
        """Check if this is a noon shift"""
        return self.shift_time == "Noon"

    @property
    def is_evening(self) -> bool:
        """Check if this is an evening shift"""
        return self.shift_time == "Evening"
    
    @property
    def is_night(self) -> bool:
        """Check if this is a night shift"""
        return self.shift_time == "Night"
    
    @property
    def shift_type(self) -> str:
        """Get the type of the shift and validate that shift type exists in the SHIFT_TYPES list"""
        shift_type = None
        if self.is_night:
            shift_type = "night"
        elif self.is_weekend_shift:
            shift_type = "weekend"
        else:
            shift_type = "regular"
        
        if shift_type not in VALID_SHIFT_TYPES:
            raise ValueError(f"Shift type \"{shift_type}\" is not a valid shift type")
        
        return shift_type

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

    def assign_person(self, person: 'Person') -> None:
        """Assign a person to this shift"""
        if person not in self.assigned_people:
            self.assigned_people.append(person)
            self.is_staffed = True if len(self.assigned_people) >= self.needed else False
    def unassign_person(self, person: 'Person') -> None:
        """Remove a person from this shift"""
        if person in self.assigned_people:
            self.assigned_people.remove(person) 
            self.is_staffed = True if len(self.assigned_people) >= self.needed else False

    def copy_with_group(self) -> 'Shift':
        """Create a copy of this shift, optionally with a new group"""
        group = self.group
        new_shift = Shift(self.shift_day, self.shift_time, group, self.needed)
        new_shift.is_staffed = self.is_staffed
        new_shift.assigned_people = self.assigned_people.copy()
        return new_shift
    
    def __repr__(self):
        return f"Shift(day={self.shift_day} time={self.shift_time})"