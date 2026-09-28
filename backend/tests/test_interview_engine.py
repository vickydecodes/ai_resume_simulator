import pytest
from app.services.interview_engine import decide_adaptation, calculate_initial_planned_questions

def test_seniority_question_planning():
    assert calculate_initial_planned_questions("Junior Developer") == 6
    assert calculate_initial_planned_questions("Senior Software Engineer") == 10
    assert calculate_initial_planned_questions("Mid-Level Backend Engineer") == 8

def test_adaptation_rules_difficulty():
    # High performance increases difficulty
    next_diff, new_total, is_final, reason = decide_adaptation(
        current_turn=2, current_planned_total=8, current_difficulty=3, last_turn_score=85.0, all_turn_scores=[80.0, 85.0]
    )
    assert next_diff == 4
    assert is_final is False

    # Low performance decreases difficulty
    next_diff, new_total, is_final, reason = decide_adaptation(
        current_turn=2, current_planned_total=8, current_difficulty=3, last_turn_score=35.0, all_turn_scores=[40.0, 35.0]
    )
    assert next_diff == 2
    assert is_final is False
