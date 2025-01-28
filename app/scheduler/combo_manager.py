from typing import List, Tuple, Set
from app.scheduler.person import Person
from app.scheduler.shift import Shift


class ComboManager:
    # Define target pairs as a class attribute
    TARGET_PAIRS = [
        {"Avishay", "Shani Keynan"},
        # {"Shani Keynan", "Eliran Ron"},
        # {"Shani Keynan", "Nir Ozery"},
        # {"Shani Keynan", "Yoram"},
        # {"Shani Keynan", "Maor"}
    ]

    def __init__(self):
        self.preferences = {
            'constraint_score': True,  # Enabled by default
            'preferred_people': False,  # Enabling target names preference
            'double_shifts': True
        }
        
        # Use the class-defined target pairs
        self.target_names = self.TARGET_PAIRS
        self.current_shift = None  # Add this to store current shift
        
    def sort_combinations(self, 
                         combinations: List[List[Person]], 
                         current_shift: Shift = None,
                         shift_group = None) -> List[List[Person]]:
        """
        Sort combinations based on enabled preferences.
        Currently implements constraint score, target names, and double shifts sorting.
        
        Args:
            combinations: List of combinations, where each combination is a list/tuple of Person objects
            current_shift: The shift being assigned (needed for double shifts preference)
            shift_group: ShiftGroup object needed for double shifts calculations
            
        Returns:
            Sorted list of combinations
            
        Raises:
            ValueError: If combinations is empty or None
        """
        if not combinations:
            raise ValueError("Cannot sort empty combinations list - this indicates a problem in the algorithm")
            
        # Store current shift for use in _calculate_constraint_score
        self.current_shift = current_shift
            
        def get_score_key(combo):
            """Generate a scoring tuple for sorting"""
            combo = list(combo) if isinstance(combo, tuple) else combo
            
            # Calculate target names score (0 or 1)
            target_names_score = int(self._has_target_names(combo)) if self.preferences['preferred_people'] else 0
            
            # Calculate constraint score
            constraint_score = self._calculate_constraint_score(combo, current_shift.shift_type)
            
            # Calculate double shifts score
            double_shifts_score = self._count_double_shifts(combo, current_shift, shift_group) if self.preferences['double_shifts'] and current_shift and shift_group else 0
            
            # Sorting priority:
            # 1. Target pairs (negative to make True come first)
            # 2. Double shifts (negative to make more double shifts come first)
            # 3. Constraint score (positive because lower/more constrained is already better)
            return (-target_names_score, -double_shifts_score, constraint_score)
            
        # Sort combinations using the score tuple as key
        return sorted(combinations, key=get_score_key)
    
    def _calculate_constraint_score(self, combo: List[Person], shift_type: str) -> float:
        """Calculate the total constraint score for a combination."""
        if not self.preferences['constraint_score'] or not self.current_shift:
            return 0.0
        
        score_type = shift_type

        for person in combo:
            try:
                return sum(p.constraint_scores[score_type] for p in combo)
            except KeyError:
                raise KeyError(f"Missing {score_type} constraint score for person {person.name}")

    def _has_target_names(self, combo: List[Person]) -> bool:
        """Check if the combination contains any of the target name pairs."""
        names_in_combo = {p.name for p in combo}
        if self.preferences['preferred_people']:
            return any(len(names_in_combo & target_pair) == 2 for target_pair in self.target_names)
        return 0.0

    def _count_double_shifts(self, combo: List[Person], shift: Shift, shift_group) -> int:
        """Count how many people in the combo can do double shifts."""
        if not self.preferences['double_shifts']:
            return 0
        if not shift_group:
            return 0
        return sum(1 for person in combo 
                  if person.double_shift and shift_group.is_consecutive_shift(person, shift))
