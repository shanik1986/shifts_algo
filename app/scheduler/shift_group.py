from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from app.scheduler.shift import Shift
from app.scheduler.utils import debug_log

if TYPE_CHECKING:
    from app.scheduler.person import Person

class ShiftGroup:
    """Manages a group of shifts and their assignments"""
    
    def __init__(self):
        self.shifts: List[Shift] = []
        self.people: List['Person'] = []
    
    def add_shift(self, shift: Shift) -> None:
        """Add a shift to the group"""
        if shift not in self.shifts:
            self.shifts.append(shift)
            shift.group = self  # Set back-reference to this group

    def add_person(self, person: 'Person') -> None:
        """Add a person to the group"""
        if person not in self.people:
            self.people.append(person)
            person.group = self  # Set back-reference to this group

    def get_shift(self, day: str, time: str) -> Optional[Shift]:
        """Get a shift by day and time"""
        for shift in self.shifts:
            if shift.shift_day == day and shift.shift_time == time:
                return shift
        return None
    
    # The function receives a shift, and returns all the shifts from the ShiftGroup that have the same day  
    def get_all_same_day_shifts(self, tested_shift: Shift) -> List[Shift]:
        """Get all shifts from the same day as the given shift"""
        return [shift for shift in self.shifts if shift.shift_day == tested_shift.shift_day]
    
    def get_all_shifts_from_day(self, day: str) -> List[Shift]:
        return [s for s in self.shifts if s.shift_day == day]

    def is_person_assigned(self, person: 'Person', day: str, time: str) -> bool:
        """Check if a person is assigned to a specific day and time"""
        shift = self.get_shift(day, time)
        return shift is not None and person in shift.assigned_people 
    

    
    def is_morning_after_night(self, person: 'Person', shift: Shift) -> bool:
        """Check if assignment will violate morning after night constraint"""
        if shift.is_morning and shift.previous_day:
            return self.is_person_assigned(person, shift.previous_day, "Night")
        
        elif shift.is_night and shift.next_day:
            return self.is_person_assigned(person, shift.next_day, "Morning")
        
        return False
    
    def is_noon_after_night(self, person: 'Person', shift: Shift) -> bool:
        """Check if assignment will violate noon after night constraint"""
        if shift.is_noon and shift.previous_day:
            return self.is_person_assigned(person, shift.previous_day, "Night")
        elif shift.is_night and shift.next_day:
            return self.is_person_assigned(person, shift.next_day, "Noon")
        return False
    
    def is_consecutive_shift(self, person: 'Person', shift: Shift) -> bool:
        """Check if assignment will violate consecutive shift constraint"""
        if shift.previous_shift and self.is_person_assigned(person, shift.shift_day, shift.previous_shift):
            return True
        elif shift.next_shift and self.is_person_assigned(person, shift.shift_day, shift.next_shift):
            return True
        return False
    
    def is_night_after_evening(self, person: 'Person', shift: Shift) -> bool:
        """Check if assignment will violate night after evening constraint"""
        if shift.is_night and self.is_person_assigned(person, shift.shift_day, "Evening"):
            return True
        elif shift.is_evening and self.is_person_assigned(person, shift.shift_day, "Night"):
            return True
        return False
    
    def is_third_shift(self, person: 'Person', shift: Shift) -> bool:
        """Check if assignment will violate third shift constraint"""
        count = self.count_shifts_in_day(person, shift.shift_day)
        return True if count >= 2 else False
    
    def count_shifts_in_day(self, person: 'Person', day: str) -> int:
        """Count how many shifts a person has on a given day"""
        count = 0
        for shift in self.get_all_shifts_from_day(day):
            if person in shift.assigned_people:
                count += 1
        return count

    def check_all_constraints(self, person: 'Person', shift: Shift, 
                            allow_consecutive: bool, 
                            allow_three_shifts: bool, 
                            allow_night_noon: bool) -> Tuple[bool, str]:
        """
        Check all group-based constraints for a person and shift.
        Returns (is_allowed, reason_if_not_allowed)
        """
        # Morning after night
        if self.is_morning_after_night(person, shift):
            return False, "Morning after night conflict"
        
        # Night and noon
        if not allow_night_noon and self.is_noon_after_night(person, shift):
            return False, "Night and noon conflict"

        # Consecutive shifts
        if not allow_consecutive and self.is_consecutive_shift(person, shift):
            return False, "Consecutive shift not allowed"
        
        # Third shift
        if self.is_third_shift(person, shift):
            if not allow_three_shifts:
                return False, "Third shift not allowed"
            elif shift.is_evening or person.is_shift_assigned(Shift(shift.shift_day, "Evening", group=self)):
                return False, "Third shift not allowed when evening shift is assigned"
        
        # Night after evening
        if self.is_night_after_evening(person, shift):
            return False, "Night after evening conflict"

        return True, ""

    def rank_shifts(self, people: List['Person']) -> List[Shift]:
        """
        Rank shifts by two dynamic parameters:
          1) Shift type's overall ratio = (total eligible capacity) / (total needed);
             smaller ratio => more constrained => higher priority.
          2) Within that shift type, the per-shift constraint_score (lower => more constrained).
        """
        # First ensure all people have their constraint scores calculated
        for person in people:
            if not person.constraint_scores:  # If scores haven't been calculated yet
                person.calculate_constraint_score(self)
        
        # Compute dynamic ratios per shift type
        type_ratios = self.get_shift_type_ratios()

        rankings = []
        for shift in self.shifts:
            if shift.is_staffed:  # Skip already staffed shifts
                continue
            
            shift_type = shift.shift_type
            eligible_people = [p for p in people if p.is_eligible_for_shift(shift)]
            
            try:
                total_eligible_capacity = sum(
                    p.constraint_scores[shift_type] 
                    for p in eligible_people
                )
                if total_eligible_capacity < 0:
                    raise ValueError(f"Found negative constraint score for shift type {shift_type}")
            except KeyError as e:
                # Find which person(s) are missing the constraint score
                missing_score_people = [
                    (p.name, list(p.constraint_scores.keys()))
                    for p in eligible_people 
                    if shift_type not in p.constraint_scores
                ]
                raise KeyError(
                    f"Missing {shift_type} constraint score for people: {missing_score_people}"
                ) from e

            # A capacity of 0 => infinite constraint_score
            constraint_score = total_eligible_capacity / shift.needed if total_eligible_capacity > 0 else float('inf')
            
            rankings.append((constraint_score, shift))

        # Now sort using the dynamic ratio first, then the per-shift constraint_score
        def sort_key(item):
            score, shift = item
            # Use exact shift_type to match ratios dictionary
            ratio = type_ratios.get(shift.shift_type, float('inf'))
            return (ratio, score)

        sorted_rankings = sorted(rankings, key=sort_key)

        print("\n=== Ranked Shifts ===")
        for rank, (score, shift) in enumerate(sorted_rankings, 1):
            print(f"Rank {rank}: {shift} | "
                  f"Type: {shift.shift_type} (ratio={type_ratios.get(shift.shift_type, 'inf')}) | "
                  f"Score={score}")
        print("=====================\n")

        return [shift for _, shift in sorted_rankings] 
    
    def get_remaining_shift_types(self) -> List[str]:
        unstaffed_shifts = [s for s in self.shifts if not s.is_staffed]
        return list(set([shift.shift_type for shift in unstaffed_shifts]))

    def get_shift_type_ratios(self) -> Dict[str, float]:
        # Get unstaffed shifts
        unstaffed_shifts = [s for s in self.shifts if not s.is_staffed]

        # Create a set of keys that represent remaining shift types
        remaining_shift_types = self.get_remaining_shift_types()
        

        # Create a dict where the keys are shift types and the values are the type's constraint score calculated by: 
        # (sum of all eligible remaining capacity for this shift type) / (total needed for this shift type)
        shift_type_ratios = {}
        for shift_type in remaining_shift_types:
            total_needed = sum(shift.needed for shift in unstaffed_shifts if shift.shift_type == shift_type)
            eligible_capacity = self.get_eligible_capacity_by_type(shift_type)
            shift_type_ratios[shift_type] = eligible_capacity / total_needed
        
        return shift_type_ratios

    def get_eligible_capacity_by_type(self, shift_type: str) -> float:
        eligible_capacity = 0
        unstaffed_shifts = [s for s in self.shifts if not s.is_staffed]
        for shift in unstaffed_shifts:
            if shift.shift_type == shift_type:
                eligible_capacity += sum(p.get_capacity_by_type(shift_type) for p in self.people if p.is_eligible_for_shift(shift))
        return eligible_capacity

