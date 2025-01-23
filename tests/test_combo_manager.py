import pytest
from app.scheduler.combo_manager import ComboManager
from app.scheduler.person import Person


def test_empty_combinations(combo_manager):
    """Test that empty combinations list raises ValueError"""
    with pytest.raises(ValueError, match="Cannot sort empty combinations list"):
        combo_manager.sort_combinations([])

def test_constraint_score_sorting(combo_manager, sample_combination_list_from_people):
    """
    Test that combinations are sorted by total constraint score.
    The expected order is:
    [
        [p4, p5], # 9
        [p3, p5], # 8
        [p2, p5], # 7.1
        [p1, p5], # 7
        [p3, p4], # 5
        [p2, p4], # 4.1
        [p1, p4], # 4
        [p2, p3], # 3.1
        [p1, p3], # 3
        [p1, p2]  # 2.1
    ]
    """
    sorted_combos = combo_manager.sort_combinations(sample_combination_list_from_people)
    
    # The combinations should be sorted by ascending constraint score
    previous_score = -float('inf')
    for combo in sorted_combos:
        current_score = sum(person.constraints_score for person in combo)
        assert current_score >= previous_score, "Combinations not properly sorted by constraint score"
        previous_score = current_score

def test_disable_constraint_score(combo_manager, sample_people):
    """Test that disabling constraint score preference maintains original order"""
    p1, p2, p3, p4, p5 = sample_people
    
    combinations = [
        [p4, p5], # 9
        [p3, p5], # 8
        [p2, p5], # 7.1
        [p1, p5], # 7
        [p3, p4], # 5
        [p2, p4], # 4.1
        [p1, p4], # 4
        [p2, p3], # 3.1
        [p1, p3], # 3
        [p1, p2]  # 2.1
    ]
    
    # Disable constraint score preference
    combo_manager.preferences['constraint_score'] = False
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    # Order should remain unchanged when constraint score is disabled
    assert sorted_combos == combinations 

def test_target_names_structure(combo_manager, target_names_people_with_same_constraint_score):
    """Test that target_names structure matches between fixture and ComboManager"""
    fixture_pairs = target_names_people_with_same_constraint_score['target_pairs']
    assert combo_manager.target_names == fixture_pairs

def test_target_names_sorting(combo_manager, target_names_people_with_same_constraint_score):
    """Test that combinations with target pairs are prioritized"""
    people = target_names_people_with_same_constraint_score['people']
    # Create combinations with and without target pairs
    target_pair_combo = [people['avishay'], people['shani']]  # Should be first (matches target pair)
    non_target_combo = [people['other'], people['nir']]       # Should be last (no target pair)
    
    combinations = [non_target_combo, target_pair_combo]
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    assert sorted_combos[0] == target_pair_combo
    assert sorted_combos[1] == non_target_combo

def test_target_pairs_vs_non_pairs(combo_manager, target_names_people_with_same_constraint_score):
    """Test that any target pair comes before non-target pairs"""
    people = target_names_people_with_same_constraint_score['people']
    pair1 = [people['shani'], people['eliran']]  # Target pair (Shani Keynan + Eliran Ron)
    pair2 = [people['shani'], people['yoram']]   # Different target pair (Shani Keynan + Yoram)
    non_pair = [people['nir'], people['maor']]   # No target pair
    
    combinations = [non_pair, pair2, pair1]
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    # Only assert that non-pair comes last
    assert sorted_combos[2] == non_pair

def test_combined_scoring(combo_manager, target_names_people_with_same_constraint_score):
    """Test combination of target pairs and constraint scores"""
    # Set different constraint scores
    target_names_people_with_same_constraint_score['people']['avishay'].constraints_score = 2.0
    target_names_people_with_same_constraint_score['people']['shani'].constraints_score = 2.0      # Target pair but high constraints
    target_names_people_with_same_constraint_score['people']['eliran'].constraints_score = 1.0
    target_names_people_with_same_constraint_score['people']['yoram'].constraints_score = 1.0      # Better constraints but no target pair
    
    target_pair_high_constraints = [target_names_people_with_same_constraint_score['people']['avishay'], target_names_people_with_same_constraint_score['people']['shani']]    # (-1, 4.0)
    no_target_low_constraints = [target_names_people_with_same_constraint_score['people']['eliran'], target_names_people_with_same_constraint_score['people']['yoram']]        # (0, 2.0)
    
    combinations = [target_pair_high_constraints, no_target_low_constraints]
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    # Target pair should still come first despite higher constraint score
    assert sorted_combos[0] == target_pair_high_constraints
    assert sorted_combos[1] == no_target_low_constraints

def test_constraint_score_sorting_no_targets(combo_manager, target_names_people_with_same_constraint_score):
    """Test constraint score sorting when no target pairs are present"""
    # Set different constraint scores
    target_names_people_with_same_constraint_score['people']['eliran'].constraints_score = 1.0
    target_names_people_with_same_constraint_score['people']['yoram'].constraints_score = 1.0    # Total: 2.0
    target_names_people_with_same_constraint_score['people']['maor'].constraints_score = 2.0
    target_names_people_with_same_constraint_score['people']['other'].constraints_score = 2.0    # Total: 4.0
        
    better_combo = [target_names_people_with_same_constraint_score['people']['eliran'], target_names_people_with_same_constraint_score['people']['yoram']]    # Lower total constraints
    worse_combo = [target_names_people_with_same_constraint_score['people']['maor'], target_names_people_with_same_constraint_score['people']['other']]       # Higher total constraints
    
    combinations = [worse_combo, better_combo]
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    assert sorted_combos[0] == better_combo
    assert sorted_combos[1] == worse_combo

def test_preferences_disabled(combo_manager, target_names_people_with_same_constraint_score):
    """Test sorting behavior when preferences are disabled"""
    # Disable both preferences
    combo_manager.preferences['preferred_people'] = False
    combo_manager.preferences['constraint_score'] = False
    
    target_pair = [target_names_people_with_same_constraint_score['people']['avishay'], target_names_people_with_same_constraint_score['people']['shani']]
    non_target = [target_names_people_with_same_constraint_score['people']['eliran'], target_names_people_with_same_constraint_score['people']['yoram']]
    
    # Set different constraint scores
    target_names_people_with_same_constraint_score['people']['avishay'].constraints_score = 2.0
    target_names_people_with_same_constraint_score['people']['shani'].constraints_score = 2.0
    target_names_people_with_same_constraint_score['people']['eliran'].constraints_score = 1.0
    target_names_people_with_same_constraint_score['people']['yoram'].constraints_score = 1.0
    
    combinations = [target_pair, non_target]
    sorted_combos = combo_manager.sort_combinations(combinations)
    
    # Should maintain original order when preferences are disabled
    assert sorted_combos == combinations 