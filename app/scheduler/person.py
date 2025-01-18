from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from app.scheduler.utils import get_adjacent_days, get_adjacent_shifts, is_weekend_shift, debug_log


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

    def assign_to_shift(self, day: str, shift: str, current_assignments: dict):
        """Assign this person to a shift"""
        current_assignments[day][shift].append(self.name)
        self.increment_shift_count()
        if shift == "Night":
            self.increment_night_count()
        if is_weekend_shift(day, shift):
            self.weekend_shifts += 1
    
    
    def unassign_from_shift(self, day: str, shift: str, current_assignments: dict):
        """Unassign this person from a shift"""
        current_assignments[day][shift].remove(self.name)
        self.decrement_shift_count()
        if shift == "Night":
            self.decrement_night_count()
        if is_weekend_shift(day, shift):
            self.weekend_shifts -= 1
    
    # Increment shift count
    def increment_shift_count(self):
        self.shift_counts += 1
    

    # Increment night count
    def increment_night_count(self):
        self.night_counts += 1
    
    # Decrement shift count
    def decrement_shift_count(self):
        self.shift_counts -= 1
    
    # Decrement night count
    def decrement_night_count(self):
        self.night_counts -= 1
    
    def is_shift_assigned(self, day, shift, current_assignments):
        """Check if person is assigned to a shift"""
        return self.name in current_assignments[day][shift]
    
    
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
    
    def is_morning_after_night(self, day, shift, current_assignments):
        """Check if this will be the morning shift after a night shift or night shift before a morning shift"""

        previous_day, next_day = get_adjacent_days(day)
        if previous_day and shift == "Morning":
            return self.is_shift_assigned(previous_day, "Night", current_assignments)
        
        elif next_day and shift == "Night":
            return self.is_shift_assigned(next_day, "Morning", current_assignments)
        
        return False

    
    def is_noon_after_night(self, day, shift, current_assignments):
        """Check if this will be the noon shift after a night shift or night shift before a noon shift"""
        previous_day, next_day = get_adjacent_days(day)

        if previous_day and shift == "Noon":
            return self.is_shift_assigned(previous_day, "Night", current_assignments)
        elif next_day and shift == "Night":
            return self.is_shift_assigned(next_day, "Noon", current_assignments)
        return False
    
    
    def is_consequtive_shift(self, day, shift, current_assignments):
        """Check if this will be the consequtive shift"""
        previous_shift, next_shift = get_adjacent_shifts(shift)
        if next_shift and self.is_shift_assigned(day, next_shift, current_assignments):
            return True
        elif previous_shift and self.is_shift_assigned(day, previous_shift, current_assignments):
            return True
        return False
    
    def is_third_shift(self, day, current_assignments):
        """Check if this is the third shift of the day"""
        counter = 0
        for assigned_people in current_assignments[day].values():
            if self.name in assigned_people:
                counter+=1
        return counter >=2

    def is_night_after_evening(self, day, shift, current_assignments):
        """
        Check if this will be the night shift after an evening shift
        Function should only accept "Night" or "Evening" as arguments
        """
        if shift == "Night":
            return self.is_shift_assigned(day, "Evening", current_assignments)
        elif shift == "Evening":
            return self.is_shift_assigned(day, "Night", current_assignments)
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
        if self.is_max_nights_reached() and shift == "Night":
            debug_log(base_msg + "Not available - Maximum night shifts reached")
            return False
        
        # Check if this will be the morning shift after a night shift or night shift before a morning shift
        if self.is_morning_after_night(day, shift, current_assignments):
            debug_log(base_msg + "Not available - Morning after night/Night before morning conflict")
            return False
        
        # Check Night before Noon constraint
        if not(self.night_and_noon_possible) and self.is_noon_after_night(day, shift, current_assignments):
            debug_log(base_msg + "Not available - Night and noon conflict")
            return False

        # Check if this is a consecutive shift and the person is not allowed to have double shifts
        if not(self.double_shift) and self.is_consequtive_shift(day, shift, current_assignments):
            debug_log(base_msg + "Not available - Consecutive shift not allowed")
            return False        
        
        # Check if this is the third shift of the day and the person is not allowed to have three shifts
        if self.is_third_shift(day, current_assignments):
            if not(self.are_three_shifts_possible) or shift == "Evening" or self.is_shift_assigned(day, "Evening", current_assignments):
                debug_log(base_msg + "Not available - Third shift not allowed")
                return False
        
        # Check if this is the night shift after an evening shift
        if (shift == "Night" or shift == "Evening") and self.is_night_after_evening(day, shift, current_assignments):
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
