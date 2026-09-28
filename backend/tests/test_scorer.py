import pytest
from app.services.scorer import compute_calibrated_selection_probability, calculate_resume_role_fit

def test_resume_role_fit_calculation():
    resume_skills = ["Python", "FastAPI", "React", "Docker"]
    role_skills = ["Python", "FastAPI", "MongoDB", "Kubernetes"]
    fit = calculate_resume_role_fit(resume_skills, role_skills)
    assert 40.0 <= fit <= 100.0

def test_probability_calibration_curve():
    # Test high score mapping
    prob_high = compute_calibrated_selection_probability(overall_score=88.0, resume_fit_score=85.0)
    assert prob_high > 70.0

    # Test baseline score mapping (approx ~50%)
    prob_mid = compute_calibrated_selection_probability(overall_score=70.0, resume_fit_score=70.0)
    assert 45.0 <= prob_mid <= 55.0

    # Test low score mapping
    prob_low = compute_calibrated_selection_probability(overall_score=45.0, resume_fit_score=40.0)
    assert prob_low < 30.0
