from typing import List, Tuple
from app.scheduler.person import Person
from app.scheduler.shift import Shift


class ComboManager:
    def __init__(self):
        self.preferences = {
            'constraint_score': True,  # Enabled by default
            'preferred_people': False,
            'double_shifts': False
        }
        
    def sort_combinations(self, 
                         combinations: List[List[Person]], 
                         current_shift: Shift = None) -> List[List[Person]]:
        """
        Sort combinations based on enabled preferences.
        Currently only implements constraint score sorting.
        
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
            
        # Calculate scores for each combination
        scored_combos = []
        for combo in combinations:
            # Convert tuple to list if necessary
            combo = list(combo) if isinstance(combo, tuple) else combo
            score = self._calculate_combo_score(combo)
            scored_combos.append((score, combo))
            
        # Sort by score (higher scores first)
        scored_combos.sort(key=lambda x: x[0], reverse=True)
        
        # Return just the combinations without scores
        return [combo for _, combo in scored_combos]
    
    def _calculate_combo_score(self, combo: List[Person]) -> float:
        """
        Calculate the total score for a combination.
        Currently only considers constraint scores.
        """
        if self.preferences['constraint_score']:
            return sum(person.constraints_score for person in combo)
        return 0
