from src.TextExtraction.JobDescriptionExtraction import JobDescriptionParser

def test_parser_runs_on_sample():
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
    result = parser.parse(sample_text)
    assert result.get("job_title"), "job_title should not be empty"
    assert result.get("location"), "location should not be empty"
    assert "skills" in result and isinstance(result["skills"], list), "skills should be a list"
    assert "ats_score" in result and isinstance(result["ats_score"], dict), "ats_score should be a dict"
