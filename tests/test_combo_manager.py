import pytest
from app.scheduler.combo_manager import ComboManager
from app.scheduler.person import Person


def test_empty_combinations(combo_manager):
    """Test that empty combinations raise ValueError"""
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