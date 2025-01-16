from dataclasses import dataclass
from typing import List, Tuple

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
            night_and_noon_possible=person_dict['night_and_noon_possible']
        )

    
    
    
    def is_shift_blocked(self, day: str, shift: str) -> bool:
        """
        Check if shift is in person's unavailable shifts
        Returns True if the shift is blocked, False otherwise
        """
        return (day, shift) in self.unavailable 
    
    # Print the person's name when the object is printed
    def __repr__(self):
        return f"Person(name={self.name})"


