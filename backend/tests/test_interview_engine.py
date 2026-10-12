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

def test_tech_and_sales_20_questions():
    from app.services.interview_engine import generate_all_questions_for_session

    # 1. Tech session test
    tech_session = {
        "session_id": "test-tech",
        "role_analysis": {"role_title": "Senior Backend Engineer"},
        "company_info": {"company_name": "Stripe"},
        "difficulty_level": "medium",
        "total_questions_planned": 20
    }
    tech_questions = generate_all_questions_for_session(tech_session)
    assert len(tech_questions) == 20
    assert tech_questions[0]["stage_category"] == "aptitude"
    assert tech_questions[10]["stage_category"] == "technical"
    # Ensure no coding questions exist
    assert all(q["question_type"] != "coding" for q in tech_questions)

    # 2. Sales / Non-tech session test
    sales_session = {
        "session_id": "test-sales",
        "role_analysis": {"role_title": "Enterprise Account Executive"},
        "company_info": {"company_name": "Salesforce"},
        "difficulty_level": "hard",
        "total_questions_planned": 20
    }
    sales_questions = generate_all_questions_for_session(sales_session)
    assert len(sales_questions) == 20
    assert sales_questions[0]["stage_category"] == "aptitude"
    assert sales_questions[10]["stage_category"] == "domain"
    assert "Quota" in sales_questions[0]["topic"] or "Pipeline" in sales_questions[0]["topic"]
    # 3. Product Management session test
    pm_session = {
        "session_id": "test-pm",
        "role_analysis": {"role_title": "Product Manager - Payments"},
        "company_info": {"company_name": "Google"},
        "difficulty_level": "medium",
        "total_questions_planned": 20
    }
    pm_questions = generate_all_questions_for_session(pm_session)
    assert len(pm_questions) == 20
    assert pm_questions[0]["stage_category"] == "aptitude"
    assert pm_questions[10]["stage_category"] == "domain"

    # 4. Data Science & ML session test
    data_session = {
        "session_id": "test-data",
        "role_analysis": {"role_title": "Senior Machine Learning Engineer"},
        "company_info": {"company_name": "Amazon"},
        "difficulty_level": "hard",
        "total_questions_planned": 20
    }
    data_questions = generate_all_questions_for_session(data_session)
    assert len(data_questions) == 20
    assert data_questions[0]["stage_category"] == "aptitude"
    assert data_questions[10]["stage_category"] == "domain"

    # 5. Finance / Consulting session test
    finance_session = {
        "session_id": "test-finance",
        "role_analysis": {"role_title": "Investment Banking Associate"},
        "company_info": {"company_name": "Goldman Sachs"},
        "difficulty_level": "medium",
        "total_questions_planned": 20
    }
    finance_questions = generate_all_questions_for_session(finance_session)
    assert len(finance_questions) == 20
    assert finance_questions[0]["stage_category"] == "aptitude"
    assert finance_questions[10]["stage_category"] == "domain"


