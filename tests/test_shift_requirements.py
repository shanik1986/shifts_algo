# Test the attributes of the shift constraints imported from the Google Sheet
def test_shift_requirements_attributes(sample_shift_constraints):
    """
    Test the attributes of the shift constraints imported from the Google Sheet
    The shift constraints are imported from the Google Sheet and processed into a dictionary
    """
    assert "Morning" not in sample_shift_constraints["Last Saturday"]
    assert "Noon" not in sample_shift_constraints["Last Saturday"]
    assert "Evening" not in sample_shift_constraints["Last Saturday"]
    assert sample_shift_constraints["Last Saturday"]["Night"] == 3
    assert sample_shift_constraints["Sunday"]["Morning"] == 3
    assert sample_shift_constraints["Sunday"]["Noon"] == 3
    assert sample_shift_constraints["Sunday"]["Evening"] == 3
    assert sample_shift_constraints["Sunday"]["Night"] == 3
    assert sample_shift_constraints["Monday"]["Morning"] == 3
    assert sample_shift_constraints["Monday"]["Noon"] == 3
    assert sample_shift_constraints["Monday"]["Evening"] == 3
    assert sample_shift_constraints["Monday"]["Night"] == 3
    assert sample_shift_constraints["Tuesday"]["Morning"] == 2
    assert sample_shift_constraints["Tuesday"]["Noon"] == 4
    assert sample_shift_constraints["Tuesday"]["Evening"] == 5
    assert sample_shift_constraints["Tuesday"]["Night"] == 2
    assert sample_shift_constraints["Wednesday"]["Morning"] == 1
    assert sample_shift_constraints["Wednesday"]["Noon"] == 1
    assert "Evening" not in sample_shift_constraints["Wednesday"]
    assert sample_shift_constraints["Wednesday"]["Night"] == 1
    assert sample_shift_constraints["Thursday"]["Morning"] == 1
    assert sample_shift_constraints["Thursday"]["Noon"] == 1
    assert sample_shift_constraints["Thursday"]["Evening"] == 1
    assert sample_shift_constraints["Thursday"]["Night"] == 1
    assert sample_shift_constraints["Friday"]["Morning"] == 1
    assert sample_shift_constraints["Friday"]["Noon"] == 1
    assert sample_shift_constraints["Friday"]["Evening"] == 1
    assert sample_shift_constraints["Friday"]["Night"] == 1
    assert sample_shift_constraints["Saturday"]["Morning"] == 3
    assert sample_shift_constraints["Saturday"]["Noon"] == 3
    assert sample_shift_constraints["Saturday"]["Evening"] == 3
    assert "Night" not in sample_shift_constraints["Saturday"]
