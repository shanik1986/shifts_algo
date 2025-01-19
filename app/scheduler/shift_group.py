from typing import Dict, List, Optional, Tuple
from app.scheduler.shift import Shift
from app.scheduler.person import Person

class ShiftGroup:
    """Manages a group of shifts and their assignments"""
    
    def __init__(self):
        self.shifts: List[Shift] = []
    
    def add_shift(self, shift: Shift) -> None:
        """Add a shift to the group"""
        if shift not in self.shifts:
            self.shifts.append(shift)
            shift.group = self  # Set back-reference to this group

    def get_shift(self, day: str, time: str) -> Optional[Shift]:
        """Get a shift by day and time"""
        for shift in self.shifts:
            if shift.shift_day == day and shift.shift_time == time:
                return shift
        return None
    
    # The function receives a shift, and returns all the shifts from the ShiftGroup that have the same day  
    def get_all_same_day_shifts(self, shift: Shift) -> List[Shift]:
        return [s for s in self.shifts if s.shift_day == shift.shift_day]

    def is_person_assigned(self, person: Person, day: str, time: str) -> bool:
        """Check if a person is assigned to a specific day and time"""
        shift = self.get_shift(day, time)
        return shift is not None and person in shift.assigned_people 
    

    
    def is_morning_after_night(self, person: Person, shift: Shift) -> bool:
        """Check if assignment will violate morning after night constraint"""
        if shift.is_morning and shift.previous_day:
            return self.is_person_assigned(person, shift.previous_day, "Night")
        
        elif shift.is_night and shift.next_day:
            return self.is_person_assigned(person, shift.next_day, "Morning")
        
        return False
    
    def is_noon_after_night(self, person: Person, shift: Shift) -> bool:
        """Check if assignment will violate noon after night constraint"""
        if shift.is_noon and shift.previous_day:
            return self.is_person_assigned(person, shift.previous_day, "Night")
        elif shift.is_night and shift.next_day:
            return self.is_person_assigned(person, shift.next_day, "Noon")
        return False
    
    def is_consecutive_shift(self, person: Person, shift: Shift) -> bool:
        """Check if assignment will violate consecutive shift constraint"""
        if shift.previous_shift and self.is_person_assigned(person, shift.shift_day, shift.previous_shift):
            return True
        elif shift.next_shift and self.is_person_assigned(person, shift.shift_day, shift.next_shift):
            return True
        return False
    
    def is_third_shift(self, person: Person, shift: Shift) -> bool:
        """Check if assignment will violate third shift constraint"""
        count = self.count_shifts_in_day(person, shift.shift_day)
        return count >= 2 and shift.is_evening
    
    def count_shifts_in_day(self, person: Person, day: str) -> int:
        """Count how many shifts a person has on a given day"""
        count = 0
        for shift in self.get_all_same_day_shifts(day):
            if person in shift.assigned_people:
                count += 1
        return count 
        return count 

    def check_all_constraints(self, person: Person, shift: Shift, 
                            allow_consecutive: bool = False, 
                            allow_three_shifts: bool = False, 
                            allow_night_noon: bool = False) -> Tuple[bool, str]:
        """
        Check all group-based constraints for a person and shift.
        Returns (is_allowed, reason_if_not_allowed)
        """
        # Morning after night
        if not self.is_morning_after_night(person, shift):
            return False, "Morning after night conflict"
        
        # Night and noon
        if not allow_night_noon and not self.is_noon_after_night(person, shift):
            return False, "Night and noon conflict"

        # Consecutive shifts
        if not allow_consecutive and self.is_consecutive_shift(person, shift):
            return False, "Consecutive shift not allowed"
        
        # Third shift
        if self.count_shifts_in_day(person, shift.shift_day) >= 2:
            if not allow_three_shifts or shift.is_evening:
                return False, "Third shift not allowed"
        
        # Night after evening
        if shift.is_night and self.is_person_assigned(person, shift.shift_day, "Evening"):
            return False, "Night after evening conflict"
        elif shift.is_evening and self.is_person_assigned(person, shift.shift_day, "Night"):
            return False, "Night after evening conflict"

        return True, "" 