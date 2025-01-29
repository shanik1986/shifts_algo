class FlagManager:
    """Manages global flags that control which constraints and preferences are enforced by the algorithm"""
    
    def __init__(self):
        # Constraint flags
        self.constraints = {
            'enforce_weekend_limit': True,      # Controls max_weekend_shifts constraint
            'enforce_three_shifts': True,       # Controls are_three_shifts_possible constraint
            'enforce_night_noon': False,         # Controls night_and_noon_possible constraint
            'enforce_consecutive': True,        # Controls allow_consecutive constraint
        }
        
        # Preference flags
        self.preferences = {
            'prefer_double_shifts': True,       # Prioritize combinations with double shifts
            'prefer_target_pairs': True,        # Prioritize target people pairs
            'use_constraint_scores': True,      # Use constraint scores for sorting
        }
    
    def set_constraint(self, constraint_name: str, value: bool) -> None:
        """Set a constraint's enforcement status"""
        if constraint_name not in self.constraints:
            raise ValueError(f"Unknown constraint: {constraint_name}")
        self.constraints[constraint_name] = value
    
    def is_enforced(self, constraint_name: str) -> bool:
        """Check if a constraint is currently being enforced"""
        if constraint_name not in self.constraints:
            raise ValueError(f"Unknown constraint: {constraint_name}")
        return self.constraints[constraint_name]
    
    def set_preference(self, preference_name: str, value: bool) -> None:
        """Set a preference's status"""
        if preference_name not in self.preferences:
            raise ValueError(f"Unknown preference: {preference_name}")
        self.preferences[preference_name] = value
    
    def is_preferred(self, preference_name: str) -> bool:
        """Check if a preference is currently enabled"""
        if preference_name not in self.preferences:
            raise ValueError(f"Unknown preference: {preference_name}")
        return self.preferences[preference_name] 