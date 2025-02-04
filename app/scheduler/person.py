from dataclasses import dataclass, field
from typing import List, Tuple, Dict, TYPE_CHECKING, Optional
from app.scheduler.utils import get_adjacent_days, get_adjacent_shifts, is_weekend_shift, debug_log
from app.scheduler.shift import Shift
from app.scheduler.shift import VALID_SHIFT_TYPES
if TYPE_CHECKING:
    from app.scheduler.shift_group import ShiftGroup

@dataclass
class Person:
    """Represents a person who can be assigned to shifts"""
    name: str
    unavailable: List[Shift]
    double_shift: bool
    max_shifts: int
    max_nights: int
    are_three_shifts_possible: bool
    night_and_noon_possible: bool
    max_weekend_shifts: int = 1
    shift_counts: int = 0
    night_counts: int = 0
    weekend_shifts: int = 0
    group: Optional['ShiftGroup'] = None

    
    # Add new fields for different constraint scores
    constraint_scores: Dict[str, float] = field(default_factory=dict)

    def assign_to_shift(self, shift: Shift) -> None:
        """Assign person to a shift"""
        shift.assign_person(self)
        self.shift_counts += 1
        if shift.is_night:
            self.night_counts += 1
        if shift.is_weekend_shift:
            self.weekend_shifts += 1

    def unassign_from_shift(self, shift: Shift) -> None:
        """Unassign person from a shift"""
        shift.unassign_person(self)
        self.shift_counts -= 1
        if shift.is_night:
            self.night_counts -= 1
        if shift.is_weekend_shift:
            self.weekend_shifts -= 1

    def is_shift_assigned(self, shift: Shift) -> bool:
        """Check if person is assigned to a shift"""
        return self in shift.assigned_people
    
    def is_shift_blocked(self, shift: Shift) -> bool:
        """Check if shift is in person's unavailable shifts"""
        return shift in self.unavailable
    

    def is_max_shifts_reached(self) -> bool:
        """Check if person has reached their maximum shifts"""
        return self.shift_counts >= self.max_shifts
        
    def is_max_nights_reached(self) -> bool:
        """Check if person has reached their maximum nights"""
        return self.night_counts >= self.max_nights
    
    def is_eligible_for_shift(self, shift: Shift) -> bool:
        """Determine if person is eligible for a given shift based on all constraints"""
        # base_msg = f"Checking {self.name} availability for {shift.shift_day} {shift.shift_time}: "

        # Basic constraints
        if shift.is_weekend_shift and self.weekend_shifts >= self.max_weekend_shifts:
            # debug_log(base_msg + "Not available - Weekend shift limit reached")
            return False
        
        if self.is_shift_blocked(shift):
            # debug_log(base_msg + "Not available - Shift is blocked")
            return False
        
        # Check if the person reached his max shifts
        if self.is_max_shifts_reached():
            # debug_log(base_msg + "Not available - Maximum shifts reached")
            return False
            
        # Check if the person reached their max nights
        if shift.is_night and self.is_max_nights_reached():
            # debug_log(base_msg + "Not available - Maximum night shifts reached")
            return False

        # Group constraints
        if not shift.group:
            return True

        is_allowed, reason = shift.group.check_all_constraints(
            person=self,
            shift=shift,
            allow_consecutive=self.double_shift,
            allow_three_shifts=self.are_three_shifts_possible,
            allow_night_noon=self.night_and_noon_possible
        )

        if not is_allowed:
            # debug_log(base_msg + f"Not available - {reason}")
            return False

        # debug_log(base_msg + "Available - All constraints passed")
        return True
    
    def calculate_constraint_score(self, shift_group: 'ShiftGroup') -> Dict[str, float]:
        """
        Calculate separate constraint scores for different types of shifts.
        Returns a dictionary of scores where higher score means MORE constrained.
        """
        
        # Calculate remaining capacities
        remaining_regular = self.get_remaining_capacity_by_type('regular')
        remaining_nights = self.get_remaining_capacity_by_type('night')
        remaining_weekends = self.get_remaining_capacity_by_type('weekend')
        
        # Get unstaffed shifts
        unstaffed_shifts = [s for s in shift_group.shifts if not s.is_staffed]
        

        # Count eligible shifts by type
        eligible_regular = sum(
            1 for shift in unstaffed_shifts
            if self.is_eligible_for_shift(shift) and not (shift.is_night or shift.is_weekend_shift)
        )
        
        eligible_nights = sum(
            1 for shift in unstaffed_shifts
            if self.is_eligible_for_shift(shift) and shift.is_night
        )
        
        eligible_weekends = sum(
            1 for shift in unstaffed_shifts
            if self.is_eligible_for_shift(shift) and shift.is_weekend_shift
        )
        
        # Calculate scores (lower score = more constrained)
        self.constraint_scores = {
            'regular': (eligible_regular / remaining_regular) if remaining_regular > 0 else float('inf'),
            'night': (eligible_nights / remaining_nights) if remaining_nights > 0 else float('inf'),
            'weekend': (eligible_weekends / remaining_weekends) if remaining_weekends > 0 else float('inf')
        }
        
        # Validate that all required scores exist
        self._validate_constraint_scores(self.constraint_scores)
        return self.constraint_scores

    
    def get_remaining_capacity_by_type(self, shift_type: str) -> int:
        if shift_type == 'regular':
            max_regular_shifts = self.max_shifts - self.max_nights
            regular_shift_count = self.shift_counts - self.night_counts
            return max_regular_shifts - regular_shift_count
        elif shift_type == 'night':
            return self.max_nights - self.night_counts
        elif shift_type == 'weekend':
            return self.max_weekend_shifts - self.weekend_shifts
        else:
            raise ValueError(f"Invalid shift type: {shift_type}")
        
        
    def __repr__(self):
        # Print the person's name when the object is printed
        return f"Person(name={self.name})"

    def _validate_constraint_scores(self, scores: Dict[str, float]) -> None:
        """Validate constraint scores"""
        # Check for missing scores
        required_scores = set(VALID_SHIFT_TYPES)
        missing_scores = required_scores - set(scores.keys())
        if missing_scores:
            raise ValueError(f"Missing constraint scores {missing_scores} for person {self.name}")
        
        # Check for invalid score types
        if not all(key in VALID_SHIFT_TYPES for key in scores.keys()):
            raise ValueError(f"Invalid constraint score keys for person {self.name}: {scores.keys()}")
