# tests/test_parser.py
from src.TextExtraction.JobDescriptionExtraction import JobDescriptionParser

def test_parser_on_sample_text():
    parser = JobDescriptionParser()
    sample_text = '''Job Title: Software Engineer
    Company: TechCorp
    Location: Austin, TX
    Responsibilities:
    - Write code
    - Collaborate with team
    Qualifications:
    - Bachelor's degree in CS
    Experience: 2+ years of experience
    Benefits: Health insurance, 401k
    Job Type: Full-time
    '''
    result = parser.parse(sample_text)
    assert result["job_title"].lower() == "data scientist"
    assert "San Francisco" in result["location"]
    assert "Python" not in result["skills"] 
    assert isinstance(result["ats_score"], dict)
