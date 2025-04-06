import sys
import os
import json
from glob import glob
from unittest.mock import patch
import src.TextExtraction.ResumeDetailsExtraction as resume_module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

mock_llm_output = {
    "choices": [{
        "text": json.dumps({
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone_number": "(123) 456-7890",
            "skills": {"technical_skills": ["Python", "Django"], "soft_skills": ["Team""work", "Problem Solving"]}, 
            "education": [{"degree": "B.Sc. in CS", "institution": "XYZ University", "year": "2018"}],
            "work_experience": [{"company": "TechCorp", "position": "Software Engineer", "duration": "2020 - Present"}],
            "languages": ["English"]
        })
    }]
}

def get_any_pdf_file():
    files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'files'))
    pdfs = glob(os.path.join(files_dir, '*.pdf'))
    if not pdfs:
        raise FileNotFoundError("❌ No PDF files found in src/files/")
    return os.path.join(files_dir, os.path.basename(pdfs[0]))

@patch("tests.test_resume_details_extraction.resume_module.extract_resume_with_llm", return_value=mock_llm_output)
def test_resume_parsing(mock_llm):
    filename = get_any_pdf_file()
    text = resume_module.extract_text_from_pdf(filename)
    result = resume_module.extract_resume_with_llm(text)
    parsed_result = json.loads(result["choices"][0]["text"])
    structured = resume_module.build_structured_resume(parsed_result)
    assert structured["full_name"] == "Jane Smith"
    assert isinstance(structured["skills"]["technical_skills"], list)
    assert "education" in structured
    assert "languages" in structured
    print("✅ Test Passed. Structured Resume:")
    print(json.dumps(structured, indent=2))