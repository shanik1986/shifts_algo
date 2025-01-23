from typing import List, Tuple, Set
from app.scheduler.person import Person
from app.scheduler.shift import Shift


class ComboManager:
    def __init__(self):
        self.preferences = {
            'constraint_score': True,  # Enabled by default
            'preferred_people': True,  # Enabling target names preference
            'double_shifts': False
        }
        
        # Define target name pairs
        self.target_names = [
            {"Avishay", "Shani Keynan"},
            # {"Shani Keynan", "Eliran Ron"},
            # {"Shani Keynan", "Nir Ozery"},
            # {"Shani Keynan", "Yoram"},
            # {"Shani Keynan", "Maor"}
        ]
        
    def sort_combinations(self, 
                         combinations: List[List[Person]], 
                         current_shift: Shift = None) -> List[List[Person]]:
        """
        Sort combinations based on enabled preferences.
        Currently implements constraint score and target names sorting.
                Args:
            combinations: List of combinations, where each combination is a list/tuple of Person objects
            current_shift: The shift being assigned (needed for double shifts preference)
            
        Returns:
            Sorted list of combinations
            
        Raises:
            ValueError: If combinations is empty or None
        """
        if not combinations:
            raise ValueError("Cannot sort empty combinations list - this indicates a problem in the algorithm")
            
        def get_score_key(combo):
            """Generate a scoring tuple for sorting"""
            combo = list(combo) if isinstance(combo, tuple) else combo
            constraint_score = self._calculate_constraint_score(combo)
            target_names_score = int(self._has_target_names(combo)) if self.preferences['preferred_people'] else 0
            return (-target_names_score, constraint_score)
            
        # Sort combinations using the score tuple as key
        return sorted(combinations, key=get_score_key)
    
    def _calculate_constraint_score(self, combo: List[Person]) -> float:
        """Calculate the total constraint score for a combination."""
        if self.preferences['constraint_score']:
            return sum(person.constraints_score for person in combo)
        return 0.0

    def _has_target_names(self, combo: List[Person]) -> bool:
        """Check if the combination contains any of the target name pairs."""
        names_in_combo = {p.name for p in combo}
        return any(len(names_in_combo & target_pair) == 2 for target_pair in self.target_names)
