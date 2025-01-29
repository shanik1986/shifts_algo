from typing import Callable, List, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from functools import partial

if TYPE_CHECKING:
    from app.scheduler.person import Person
    from app.scheduler.shift import Shift
    from app.scheduler.shift_group import ShiftGroup

@dataclass
class Constraint:
    """Represents a single constraint check"""
    check_function: Callable[['Person', 'Shift'], bool]
    error_message: str
    enabled: bool = True

class ConstraintManager:
    """Manages constraint checks for a person"""
    
    def __init__(self, person: 'Person'):
        self.person = person
        self.constraints: List[Constraint] = []
        self._setup_constraints()
    
    def _setup_constraints(self) -> None:
        """Setup constraints based on person's preferences"""
        # Basic constraints that always apply
        self.constraints.extend([
            Constraint(
                self._check_weekend_limit,
                "Weekend shift limit reached"
            ),
            Constraint(
                self._check_blocked_shift,
                "Shift is blocked"
            ),
            Constraint(
                self._check_max_shifts,
                "Maximum shifts reached"
            ),
            Constraint(
                self._check_max_nights,
                "Maximum night shifts reached"
            ),
            Constraint(
                self._check_morning_after_night,
                "Morning after night conflict"
            ),
            Constraint(
                self._check_night_after_evening,
                "Night after evening conflict"
            )
        ])

        # Optional constraints based on person preferences
        if not self.person.double_shift:
            self.constraints.append(
                Constraint(
                    self._check_consecutive_shifts,
                    "Consecutive shifts not allowed"
                )
            )
            
        if not self.person.are_three_shifts_possible:
            self.constraints.append(
                Constraint(
                    self._check_third_shift,
                    "Third shift not allowed"
                )
            )
            
        if not self.person.night_and_noon_possible:
            self.constraints.append(
                Constraint(
                    self._check_noon_after_night,
                    "Night and noon conflict"
                )
            )

    def check_all_constraints(self, shift: 'Shift') -> Tuple[bool, str]:
        """Check all enabled constraints for this person"""
        for constraint in self.constraints:
            if constraint.enabled and constraint.check_function(self.person, shift):
                return False, constraint.error_message
        return True, ""

    # Individual constraint check methods
    def _check_weekend_limit(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.is_weekend_shift and person.weekend_shifts >= person.max_weekend_shifts

    def _check_blocked_shift(self, person: 'Person', shift: 'Shift') -> bool:
        return person.is_shift_blocked(shift)

    def _check_max_shifts(self, person: 'Person', shift: 'Shift') -> bool:
        return person.is_max_shifts_reached()

    def _check_max_nights(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.is_night and person.is_max_nights_reached()

    def _check_morning_after_night(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.group.is_morning_after_night(person, shift)

    def _check_night_after_evening(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.group.is_night_after_evening(person, shift)

    def _check_consecutive_shifts(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.group.is_consecutive_shift(person, shift)

    def _check_third_shift(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.group.is_third_shift(person, shift)

    def _check_noon_after_night(self, person: 'Person', shift: 'Shift') -> bool:
        return shift.group.is_noon_after_night(person, shift) 