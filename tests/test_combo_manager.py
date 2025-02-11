import pytest
from app.scheduler.combo_manager import ComboManager
from app.scheduler.person import Person
from app.scheduler.shift import Shift
from app.scheduler.shift_group import ShiftGroup


def test_empty_combinations(combo_manager):
    """Test that empty combinations list raises ValueError"""
    with pytest.raises(ValueError, match="Cannot sort empty combinations list"):
        combo_manager.sort_combinations([])

def test_constraint_sum_score(combo_manager, sample_combination_list_from_people, sample_people):
    """
    Test that the constraint sum score is calculated correctly.
    """
    p1, p2, p3, p4, p5 = sample_people

    combinations_with_expected = [
        ([p4, p5], {'regular': 9.0, 'night': 11.0, 'weekend': 0.3}),
        ([p3, p5], {'regular': 8.0, 'night': 9.0, 'weekend': 0.4}),
        ([p2, p5], {'regular': 7.1, 'night': 8.0, 'weekend': 0.5}),
        ([p1, p5], {'regular': 7.0, 'night': 7.0, 'weekend': 0.6}),
        ([p3, p4], {'regular': 5.0, 'night': 8.0, 'weekend': 0.5}),
        ([p2, p4], {'regular': 4.1, 'night': 7.0, 'weekend': 0.6}),
        ([p1, p4], {'regular': 4.0, 'night': 6.0, 'weekend': 0.7}),
        ([p2, p3], {'regular': 3.1, 'night': 5.0, 'weekend': 0.7}),
        ([p1, p3], {'regular': 3.0, 'night': 4.0, 'weekend': 0.8}),
        ([p1, p2], {'regular': 2.1, 'night': 3.0, 'weekend': 0.9})
    ]
    
    for combo, expected_scores in combinations_with_expected:
        for shift_type in ['regular', 'night', 'weekend']:
            actual_score = sum(p.constraint_scores[shift_type] for p in combo)
            assert actual_score == pytest.approx(expected_scores[shift_type]), \
                f"For {shift_type} shift, expected score {expected_scores[shift_type]} but got {actual_score} " \
                f"for combination {[p.name for p in combo]}"


def test_constraint_score_sorting(combo_manager, sample_combination_list_from_people, sample_people):
    """
    Test that combinations are sorted by constraint score based on shift type.
    Tests regular, night, and weekend shift sorting separately.
    """
    group = ShiftGroup()
    # Test regular shift sorting
    regular_shift = Shift("Monday", "Morning", group=group)
    night_shift = Shift("Monday", "Night", group=group)
    weekend_shift = Shift("Saturday", "Morning", group=group)

    group.shifts = [regular_shift, night_shift, weekend_shift]
    for p in sample_people:
        p.calculate_constraint_score(group)



    sorted_regular = combo_manager.sort_combinations(
        sample_combination_list_from_people,
        current_shift=regular_shift
    )
    
    previous_score = -float('inf')
    for combo in sorted_regular:
        current_score = sum(p.constraint_scores['regular'] for p in combo)
        assert current_score >= previous_score, "Combinations not properly sorted by regular constraint score"
        previous_score = current_score

    # Test night shift sorting
    sorted_night = combo_manager.sort_combinations(
        sample_combination_list_from_people,
        current_shift=night_shift
    )
    
    previous_score = -float('inf')
    for combo in sorted_night:
        current_score = sum(p.constraint_scores['night'] for p in combo)
        assert current_score >= previous_score, "Combinations not properly sorted by night constraint score"
        previous_score = current_score

    # Test weekend shift sorting
    sorted_weekend = combo_manager.sort_combinations(
        sample_combination_list_from_people,
        current_shift=weekend_shift
    )
    
    previous_score = -float('inf')
    for combo in sorted_weekend:
        current_score = sum(p.constraint_scores['weekend'] for p in combo)
        assert current_score >= previous_score, "Combinations not properly sorted by weekend constraint score"
        previous_score = current_score

def test_disable_constraint_score(combo_manager, sample_people):
    """
    Test that disabling constraint score preference maintains original order. The constraint scores are:
    p1: {'regular': 1.0, 'night': 1.0, 'weekend': 0.5}
    p2: {'regular': 1.1, 'night': 2.0, 'weekend': 0.4}
    p3: {'regular': 2.0, 'night': 3.0, 'weekend': 0.3}
    p4: {'regular': 3.0, 'night': 5.0, 'weekend': 0.9}
    p5: {'regular': 6.0, 'night': 6.0, 'weekend': 0.10}
    
    """
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    p1, p2, p3, p4, p5 = sample_people
    
    combinations = [
        [p4, p5], # {regular: 9.0, night: 11.0, weekend: 0.3}
        [p3, p5], # {regular: 8.0, night: 9.0, weekend: 0.4}
        [p2, p5], # {regular: 7.1, night: 8.0, weekend: 0.5}
        [p1, p5], # {regular: 7.0, night: 7.0, weekend: 0.6}
        [p3, p4], # {regular: 5.0, night: 8.0, weekend: 0.5}
        [p2, p4], # {regular: 4.1, night: 7.0, weekend: 0.6}
        [p1, p4], # {regular: 4.0, night: 6.0, weekend: 0.7}
        [p2, p3], # {regular: 3.1, night: 5.0, weekend: 0.7}
        [p1, p3], # {regular: 3.0, night: 4.0, weekend: 0.8}
        [p1, p2]  # {regular: 2.1, night: 3.0, weekend: 0.9}
    ]
    
    # Disable constraint score preference
    combo_manager.preferences['constraint_score'] = False
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    # Order should remain unchanged when constraint score is disabled
    assert sorted_combos == combinations 

def test_target_names_structure(combo_manager, target_names_people_with_same_constraint_score):
    """Test that target_names structure matches ComboManager's defined pairs"""
    assert combo_manager.target_names == ComboManager.TARGET_PAIRS

def test_target_names_sorting(combo_manager, target_names_people_with_same_constraint_score):
    """Test that combinations with target pairs are sorted by their weights"""

    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())

    # Enable target pairs preference and disable constraint score to isolate the test
    combo_manager.preferences['preferred_people'] = True
    combo_manager.preferences['constraint_score'] = False

    # Get highest and lowest weighted pairs
    highest_weight_pair = max(ComboManager.TARGET_PAIRS, key=lambda x: x['weight'])
    lowest_weight_pair = min(ComboManager.TARGET_PAIRS, key=lambda x: x['weight'])

    # Create people for both pairs and non-target
    highest_weight_people = [
        Person(name=name, blocked_shifts={}, double_shift=False,
              max_shifts=10, max_nights=2, are_three_shifts_possible=True,
              night_and_noon_possible=True)
        for name in highest_weight_pair['pair']
    ]
    
    lowest_weight_people = [
        Person(name=name, blocked_shifts={}, double_shift=False,
              max_shifts=10, max_nights=2, are_three_shifts_possible=True,
              night_and_noon_possible=True)
        for name in lowest_weight_pair['pair']
    ]
    
    non_target_people = [
        Person(name=f"NOT_TARGET_{i}", blocked_shifts={}, double_shift=False,
              max_shifts=10, max_nights=2, are_three_shifts_possible=True,
              night_and_noon_possible=True)
        for i in range(1, 3)
    ]
    
    # Create our combinations
    highest_weight_combo = highest_weight_people
    lowest_weight_combo = lowest_weight_people
    non_target_combo = non_target_people
    
    print("\nTARGET_PAIRS:", ComboManager.TARGET_PAIRS)
    print("Highest weight pair:", [p.name for p in highest_weight_combo], f"(weight: {highest_weight_pair['weight']})")
    print("Lowest weight pair:", [p.name for p in lowest_weight_combo], f"(weight: {lowest_weight_pair['weight']})")
    print("Non-target combo:", [p.name for p in non_target_combo])
    
    # Test all combinations in different orders
    combinations = [non_target_combo, highest_weight_combo, lowest_weight_combo]
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    print("Sorted combos:", [[p.name for p in combo] for combo in sorted_combos])
    
    # The highest weight pair should come first
    assert sorted_combos[0] == highest_weight_combo, \
        f"Expected highest weight pair {[p.name for p in highest_weight_combo]} to be first, " \
        f"but got {[p.name for p in sorted_combos[0]]}"
    
    # If the lowest weight is negative, non-target should come before it
    if lowest_weight_pair['weight'] < 0:
        assert sorted_combos[1] == non_target_combo, \
            f"Expected non-target pair to come before negative weight pair"
        assert sorted_combos[2] == lowest_weight_combo, \
            f"Expected lowest weight pair to come last"
    else:
        # If lowest weight is positive, it should come before non-target
        assert sorted_combos[1] == lowest_weight_combo, \
            f"Expected lowest weight pair to come before non-target"
        assert sorted_combos[2] == non_target_combo, \
            f"Expected non-target pair to come last"

def test_target_pairs_vs_non_pairs(combo_manager, target_names_people_with_same_constraint_score):
    """Test that any target pair comes before non-target pairs when weight is positive"""
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    # Enable target pairs preference and disable constraint score to isolate the test
    combo_manager.preferences['preferred_people'] = True
    combo_manager.preferences['constraint_score'] = False
    
    # Get a positive weight pair (should come before non-target)
    positive_weight_pair = next(
        pair for pair in ComboManager.TARGET_PAIRS 
        if pair['weight'] > 0
    )
    
    # Create people for positive weight pair and non-target
    positive_weight_people = [
        Person(name=name, blocked_shifts={}, double_shift=False, 
              max_shifts=10, max_nights=2, are_three_shifts_possible=True, 
              night_and_noon_possible=True)
        for name in positive_weight_pair['pair']
    ]
    
    non_target_people = [
        Person(name=f"NOT_TARGET_{i}", blocked_shifts={}, double_shift=False,
              max_shifts=10, max_nights=2, are_three_shifts_possible=True,
              night_and_noon_possible=True)
        for i in range(1, 3)
    ]
    
    # Create our combinations
    positive_weight_combo = positive_weight_people
    non_target_combo = non_target_people
    
    print("\nTARGET_PAIRS:", ComboManager.TARGET_PAIRS)
    print("Positive weight pair:", [p.name for p in positive_weight_combo], f"(weight: {positive_weight_pair['weight']})")
    print("Non-target combo:", [p.name for p in non_target_combo])
    
    combinations = [non_target_combo, positive_weight_combo]
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    print("Sorted combos:", [[p.name for p in combo] for combo in sorted_combos])
    
    # Positive weight pair should come before non-target
    assert sorted_combos[0] == positive_weight_combo, \
        f"Expected positive weight pair {[p.name for p in positive_weight_combo]} to be first, " \
        f"but got {[p.name for p in sorted_combos[0]]}"
    assert sorted_combos[1] == non_target_combo, \
        f"Expected non-target pair {[p.name for p in non_target_combo]} to be second, " \
        f"but got {[p.name for p in sorted_combos[1]]}"

def test_combined_scoring(combo_manager, target_names_people_with_same_constraint_score):
    """Test combination of target pairs and constraint scores"""
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    # Enable target pairs preference
    combo_manager.preferences['preferred_people'] = True
    
    people = target_names_people_with_same_constraint_score
    target_pair = next(iter(ComboManager.TARGET_PAIRS))
    
    # Create target pair combo using people with matching names
    target_pair_combo = [
        next(p for p in people if p.name == name)
        for name in target_pair
    ]
    
    # Create non-target combo using people with NOT_TARGET prefix
    non_target_combo = [
        p for p in people if p.name.startswith("NOT_TARGET_")
    ][:2]
    
    # Set different constraint scores
    for p in target_pair_combo:
        p.constraints_score = 2.0  # Target pair but high constraints
    for p in non_target_combo:
        p.constraints_score = 1.0  # Better constraints but no target pair
    
    combinations = [target_pair_combo, non_target_combo]
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    # Target pair should still come first despite higher constraint score
    assert sorted_combos[0] == target_pair_combo
    assert sorted_combos[1] == non_target_combo

def test_constraint_score_sorting_no_targets(combo_manager, target_names_people_with_same_constraint_score):
    """Test constraint score sorting when no target pairs are present"""
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    # Disable target pairs preference to ensure it doesn't interfere
    combo_manager.preferences['preferred_people'] = False
    
    people = target_names_people_with_same_constraint_score
    non_target_people = [p for p in people if p.name.startswith("NOT_TARGET_")]
    
    # Make sure we have enough non-target people
    assert len(non_target_people) >= 2, "Need at least 2 non-target people for this test"
    
    # Just use first two non-target people
    first_combo = non_target_people[:2]
    second_combo = non_target_people[:2]  # Use same people, different scores
    
    # Set different constraint scores
    for p in first_combo:
        p.constraints_score = 3.0  # Higher (better) scores
    for p in second_combo:
        p.constraints_score = 1.0  # Lower (worse) scores
    
    combinations = [second_combo, first_combo]
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    assert sorted_combos[0] == first_combo  # Higher scores should come first
    assert sorted_combos[1] == second_combo  # Lower scores should come last

def test_target_pairs_ignored_constraint_score_respected(combo_manager, target_names_people_with_same_constraint_score):
    """Test that when target pairs preference is disabled but constraint scoring is enabled,
    combinations are sorted by constraint scores regardless of target pair status"""
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    # Create two non-target people with better constraint scores
    default_args = {
        'blocked_shifts': {},
        'double_shift': False,
        'max_shifts': 10,
        'max_nights': 2,
        'are_three_shifts_possible': True,
        'night_and_noon_possible': True
    }
    
    # Create target pair combo using people with matching names
    target_pair = next(iter(ComboManager.TARGET_PAIRS))
    target_pair_combo = [
        Person(name, **default_args)
        for name in target_pair
    ]
    
    # Create non-target combo
    better_scoring_combo = [
        Person("NOT_TARGET_1", **default_args, constraint_scores={'regular': -float('inf'), 'night': 1.0, 'weekend': 0.5}),
        Person("NOT_TARGET_2", **default_args, constraint_scores={'regular': -float('inf'), 'night': 1.0, 'weekend': 0.5})
    ]
    
    # Set constraint scores
    for p in target_pair_combo:
        p.constraint_scores = {'regular': 3.0, 'night': 1.0, 'weekend': 0.5}  # Higher scores = less constrained

    
    combinations = [better_scoring_combo, target_pair_combo]
    
    # Disable target pairs preference but keep constraint scoring
    combo_manager.preferences['preferred_people'] = False
    combo_manager.preferences['constraint_score'] = True
    
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    # More constrained (lower score) should come first
    assert [p.name for p in sorted_combos[0]] == [p.name for p in better_scoring_combo]  # Lower scores first
    assert [p.name for p in sorted_combos[1]] == [p.name for p in target_pair_combo]  # Higher scores last

def test_double_shift_preference_disabled(combo_manager, double_shift_people):
    """Test that double shift capability doesn't affect sorting when preference is disabled"""
    # Create two consecutive shifts
    shift_group = ShiftGroup()
    first_shift = Shift("Sunday", "Morning", needed=2, group=shift_group)
    second_shift = Shift("Sunday", "Noon", needed=2, group=shift_group)
    shift_group.add_shift(first_shift)
    shift_group.add_shift(second_shift)
    
    # Create combinations with different double shift capabilities
    double_combo = [p for p in double_shift_people if p.double_shift][:2]
    no_double_combo = [p for p in double_shift_people if not p.double_shift][:2]
    mixed_combo = [double_combo[0], no_double_combo[0]]
    
    combinations = [no_double_combo, mixed_combo, double_combo]
    
    # With preference disabled, order should remain unchanged
    combo_manager.preferences['double_shifts'] = False
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=second_shift)
    
    assert sorted_combos == combinations

def test_double_shift_preference_enabled(combo_manager, double_shift_people):
    """Test that combinations with more double shift capable people are prioritized"""
    # Create two consecutive shifts
    shift_group = ShiftGroup()
    first_shift = Shift("Sunday", "Morning", needed=2, group=shift_group)
    second_shift = Shift("Sunday", "Noon", needed=2, group=shift_group)
    shift_group.add_shift(first_shift)
    shift_group.add_shift(second_shift)
    
    # Get people who can do double shifts
    double_shifters = [p for p in double_shift_people if p.double_shift][:2]
    
    # Assign them to first shift
    for p in double_shifters:
        p.assign_to_shift(first_shift)
    
    # Create combinations for second shift
    double_combo = double_shifters  # 2 double shifts possible (-2 score)
    no_double_combo = [p for p in double_shift_people if not p.double_shift][:2]  # 0 double shifts possible (0 score)
    mixed_combo = [double_shifters[0], no_double_combo[0]]  # 1 double shift possible (-1 score)
    
    combinations = [no_double_combo, mixed_combo, double_combo]
    
    # Enable double shifts preference
    combo_manager.preferences['double_shifts'] = True
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=second_shift, shift_group=shift_group)
    
    # Print debug info
    print("\nDouble combo:", [p.name for p in double_combo], "- can do double shifts:", [p.double_shift for p in double_combo])
    print("Mixed combo:", [p.name for p in mixed_combo], "- can do double shifts:", [p.double_shift for p in mixed_combo])
    print("No double combo:", [p.name for p in no_double_combo], "- can do double shifts:", [p.double_shift for p in no_double_combo])
    print("\nSorted combos:", [[p.name for p in combo] for combo in sorted_combos])
    
    # Should be sorted by number of possible double shifts (more double shifts come first)
    # Compare by names since we're comparing different Person objects
    assert [p.name for p in sorted_combos[0]] == [p.name for p in double_combo]  # -2 score comes first
    assert [p.name for p in sorted_combos[1]] == [p.name for p in mixed_combo]   # -1 score comes second
    assert [p.name for p in sorted_combos[2]] == [p.name for p in no_double_combo]  # 0 score comes last

def test_double_shift_with_non_consecutive_shifts(combo_manager, double_shift_people):
    """Test that double shift capability doesn't affect sorting for non-consecutive shifts"""
    # Create two non-consecutive shifts
    shift_group = ShiftGroup()
    first_shift = Shift("Sunday", "Morning", needed=2, group=shift_group)
    non_consecutive_shift = Shift("Sunday", "Night", needed=2, group=shift_group)
    shift_group.add_shift(first_shift)
    shift_group.add_shift(non_consecutive_shift)
    
    # Get people who can do double shifts
    double_shifters = [p for p in double_shift_people if p.double_shift][:2]
    
    # Assign them to first shift
    for p in double_shifters:
        p.assign_to_shift(first_shift)
    
    # Create combinations
    double_combo = double_shifters
    no_double_combo = [p for p in double_shift_people if not p.double_shift][:2]
    
    combinations = [no_double_combo, double_combo]
    
    # Even with preference enabled, order shouldn't change for non-consecutive shifts
    combo_manager.preferences['double_shifts'] = True
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=non_consecutive_shift, shift_group=shift_group)
    
    # Compare by names since we're comparing different Person objects
    assert [[p.name for p in combo] for combo in sorted_combos] == [[p.name for p in combo] for combo in combinations]

def test_preferences_disabled(combo_manager, target_names_people_with_same_constraint_score):
    """Test sorting behavior when preferences are disabled"""
    # Create a regular shift
    regular_shift = Shift("Monday", "Morning", group=ShiftGroup())
    
    people = target_names_people_with_same_constraint_score
    target_pair = next(iter(ComboManager.TARGET_PAIRS))
    
    # Create target pair combo using people with matching names
    target_pair_combo = [
        next(p for p in people if p.name == name)
        for name in target_pair
    ]
    
    # Create non-target combo using people with NOT_TARGET prefix
    non_target_combo = [
        p for p in people if p.name.startswith("NOT_TARGET_")
    ][:2]
    
    # Set different constraint scores
    for p in target_pair_combo:
        p.constraints_score = 2.0
    for p in non_target_combo:
        p.constraints_score = 1.0
    
    # Disable both preferences
    combo_manager.preferences['preferred_people'] = False
    combo_manager.preferences['constraint_score'] = False
    
    combinations = [target_pair_combo, non_target_combo]
    sorted_combos = combo_manager.sort_combinations(combinations, current_shift=regular_shift)
    
    # Should maintain original order when preferences are disabled
    assert sorted_combos == combinations 