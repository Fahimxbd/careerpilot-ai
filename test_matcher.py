from src.matcher import analyze_match, extract_skills


def test_extract_skills_handles_aliases_and_boundaries():
    text = "Built REST APIs in Python with PostgreSQL, GitHub Actions, Docker, and scikit-learn."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "SQL" in skills
    assert "REST APIs" in skills
    assert "CI/CD" in skills
    assert "Docker" in skills
    assert "scikit-learn" in skills
    assert "C" not in skills


def test_match_result_is_bounded_and_explainable():
    cv = "Python developer using FastAPI, SQL, Git, Docker and pytest."
    job = "Junior Python developer needed for FastAPI REST APIs, SQL, Git, Docker and automated testing."
    result = analyze_match(cv, job)
    assert 0 <= result.overall_score <= 100
    assert result.overall_score >= 50
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills
    assert isinstance(result.recommendations, list)
    assert result.recommendations


def test_empty_input_does_not_crash():
    result = analyze_match("", "")
    assert result.overall_score == 0
    assert result.text_similarity == 0
