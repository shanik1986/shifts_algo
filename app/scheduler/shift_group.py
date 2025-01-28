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
                            allow_consecutive: bool = False, 
                            allow_three_shifts: bool = False, 
                            allow_night_noon: bool = False) -> Tuple[bool, str]:
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
        Rank shifts by their constraint level: available people / needed.
        Returns a sorted list of shifts, with most constrained first.
        """
        rankings = []
        for shift in self.shifts:
            if shift.is_staffed:  # Skip already staffed shifts
                continue
                
            # Get eligible people for this shift
            eligible_people = [p for p in people if p.is_eligible_for_shift(shift)]
            
            if eligible_people:
                constraint_score = len(eligible_people) / shift.needed
            else:
                constraint_score = 0
                
            rankings.append((constraint_score, shift))
            print(f"Shift: {shift}, Needed: {shift.needed}, "
                  f"Available people: {len(eligible_people)}, Score: {constraint_score}")

        sorted_rankings = sorted(rankings, key=lambda x: x[0])  # Sort by constraint score

        print("\n=== Ranked Shifts ===")
        for rank, (score, shift) in enumerate(sorted_rankings, 1):
            print(f"Rank {rank}: {shift} with score {score}")
        print("=====================\n")
        
        # Return just the sorted shifts
        return [shift for _, shift in sorted_rankings] 