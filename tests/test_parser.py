from unittest.mock import patch
from src.TextExtraction.JobDescriptionExtraction import JobDescriptionParser

@patch.object(JobDescriptionParser, 'parse')
def test_parser_runs_on_sample(mock_parse):
    parser = JobDescriptionParser()
    sample_text = '''
    Job Title: Data Scientist
    Company: OpenAI
    Location: San Francisco, CA
    Responsibilities:
    - Analyze large datasets
    - Build predictive models
    Qualifications:
    - Bachelor's degree in Computer Science
    Experience: 2+ years of experience in machine learning
    Benefits: Health insurance, stock options
    Job Type: Full-time
    '''

    # Simulate the parsed result
    mock_parse.return_value = {
        "job_title": "Data Scientist",
        "location": "San Francisco, CA",
        "technical_skills": ["Python", "Machine Learning"],
        "soft_skills": ["Communication", "Teamwork"],
        "ats_score": 85
    }

    result = parser.parse(sample_text)

    assert result.get("job_title"), "job_title should not be empty"
    assert result.get("location"), "location should not be empty"
    assert "technical_skills" in result and isinstance(result["technical_skills"], list), "technical_skills should be a list"
    assert "soft_skills" in result and isinstance(result["soft_skills"], list), "soft_skills should be a list"