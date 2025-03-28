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
    assert result["job_title"].lower() == "data scientist"
    assert "San Francisco" in result["location"]
    assert "Python" not in result["skills"]  # It's not mentioned in the text
    assert isinstance(result["ats_score"], dict)
