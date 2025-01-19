from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from app.scheduler.utils import get_adjacent_days, get_adjacent_shifts, is_weekend_shift, debug_log
from app.scheduler.shift import Shift


@dataclass
class Person:
    """Represents a person who can be assigned to shifts"""
    name: str
    unavailable: List[Tuple[str, str]]
    double_shift: bool
    max_shifts: int
    max_nights: int
    are_three_shifts_possible: bool
    night_and_noon_possible: bool
    max_weekend_shifts: int = 1
    shift_counts: int = 0
    night_counts: int = 0
    weekend_shifts: int = 0
    constraints_score: float = 0
    

    @classmethod
    def from_dict(cls, person_dict: dict) -> 'Person':
        """
        Converts a "person" dictionary into a Person object
        """
        return Person(
            name=person_dict['name'],
            unavailable=person_dict['unavailable'],
            double_shift=person_dict['double_shift'],
            max_shifts=person_dict['max_shifts'],
            max_nights=person_dict['max_nights'],
            are_three_shifts_possible=person_dict['are_three_shifts_possible'],
            night_and_noon_possible=person_dict['night_and_noon_possible'],
            max_weekend_shifts=person_dict.get('max_weekend_shifts', 1),
            shift_counts=person_dict.get('shift_counts', 0),
            night_counts=person_dict.get('night_counts', 0),
            weekend_shifts=person_dict.get('weekend_shifts', 0)
        )

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
    
    def is_shift_blocked(self, day: str, shift: str) -> bool:
        """
        Check if shift is in person's unavailable shifts
        Returns True if the shift is blocked, False otherwise
        """
        return (day, shift) in self.unavailable 
    

    def is_max_shifts_reached(self) -> bool:
        """Check if person has reached their maximum shifts"""
        return self.shift_counts >= self.max_shifts
        
    def is_max_nights_reached(self) -> bool:
        """Check if person has reached their maximum nights"""
        return self.night_counts >= self.max_nights
    
    def is_morning_after_night(self, shift: Shift, current_assignments) -> bool:
        """Check if this will be the morning shift after a night shift or night shift before a morning shift"""
        if shift.is_morning and shift.previous_day:
            return self.name in current_assignments[shift.previous_day]["Night"]
        
        elif shift.is_night and shift.next_day:
            return self.name in current_assignments[shift.next_day]["Morning"]
        
        return False

    def is_noon_after_night(self, shift: Shift, current_assignments) -> bool:
        """Check if this will be the noon shift after a night shift or night shift before a noon shift"""
        if shift.is_noon and shift.previous_day:
            return self.name in current_assignments[shift.previous_day]["Night"]
            
        elif shift.is_night and shift.next_day:
            return self.name in current_assignments[shift.next_day]["Noon"]
            
        return False
    
    def is_consecutive_shift(self, shift: Shift, current_assignments) -> bool:
        """Check if this will be the consecutive shift"""
        if shift.previous_shift:
            if self.name in current_assignments[shift.shift_day][shift.previous_shift]:
                return True
                
        if shift.next_shift:
            if self.name in current_assignments[shift.shift_day][shift.next_shift]:
                return True
                
        return False

    def is_third_shift(self, day, current_assignments):
        """Check if this is the third shift of the day"""
        counter = 0
        for assigned_people in current_assignments[day].values():
            if self.name in assigned_people:
                counter+=1
        return counter >=2

    def is_night_after_evening(self, shift: Shift, current_assignments) -> bool:
        """Check if this will be the night shift after an evening shift or evening before night"""
        if shift.is_night:
            return self.name in current_assignments[shift.shift_day]["Evening"]
            
        elif shift.is_evening:
            return self.name in current_assignments[shift.shift_day]["Night"]
            
        return False


    # Print the person's name when the object is printed
    def __repr__(self):
        return f"Person(name={self.name})"
    

    def is_eligible_for_shift(self, day: str, shift: str, current_assignments: dict) -> bool:
        """Determine if person is eligible for a given shift based on all constraints"""
        base_msg = f"Checking {self.name} availability for {day} {shift}: "

        # Check if this would exceed weekend shift limit
        if is_weekend_shift(day, shift) and self.weekend_shifts >= self.max_weekend_shifts:
            debug_log(base_msg + "Not available - Weekend shift limit reached")
            return False
            
        # Check if the shift is unavailable
        if self.is_shift_blocked(day, shift):
            debug_log(base_msg + "Not available - Shift is blocked")
            return False
        
        # Check if the person reached his max shifts
        if self.is_max_shifts_reached():
            debug_log(base_msg + "Not available - Maximum shifts reached")
            return False
            
        # Check if the person reached his max nights
        if self.is_max_nights_reached() and shift.is_night:
            debug_log(base_msg + "Not available - Maximum night shifts reached")
            return False
        
        # Check if this will be the morning shift after a night shift or night shift before a morning shift
        if self.is_morning_after_night(shift, current_assignments):
            debug_log(base_msg + "Not available - Morning after night/Night before morning conflict")
            return False
        
        # Check Night before Noon constraint
        if not(self.night_and_noon_possible) and self.is_noon_after_night(shift, current_assignments):
            debug_log(base_msg + "Not available - Night and noon conflict")
            return False

        # Check if this is a consecutive shift and the person is not allowed to have double shifts
        if not(self.double_shift) and self.is_consecutive_shift(shift, current_assignments):
            debug_log(base_msg + "Not available - Consecutive shift not allowed")
            return False        
        
        # Check if this is the third shift of the day and the person is not allowed to have three shifts
        if self.is_third_shift(day, current_assignments):
            if not(self.are_three_shifts_possible) or shift == "Evening" or self.is_shift_assigned(day, "Evening", current_assignments):
                debug_log(base_msg + "Not available - Third shift not allowed")
                return False
        
        # Check if this is the night shift after an evening shift
        if (shift == "Night" or shift == "Evening") and self.is_night_after_evening(shift, current_assignments):
            debug_log(base_msg + "Not available - Night after evening/Evening before night conflict")
            return False

        debug_log(base_msg + "Available - All constraints passed")
        return True
    
    def calculate_constraint_score(self, remaining_shifts: List[Tuple[str, str, int]], 
                                 current_assignments: dict) -> float:
        """
        Calculate how constrained this person is for future assignments.
        This is calculated by the number of eligible shifts divided by the remaining capacity.
        """
        remaining_capacity = self.max_shifts - self.shift_counts            
        
        eligible_shift_count = sum(
            1 for day, shift, _ in remaining_shifts
            if self.is_eligible_for_shift(day, shift, current_assignments)
        )
        
        self.constraints_score = eligible_shift_count / remaining_capacity if remaining_capacity > 0 else float("inf")
        return self.constraints_score
