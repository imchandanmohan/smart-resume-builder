import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import json
from glob import glob
from unittest.mock import patch

from TextExtraction.ResumeDetailsExtraction import (
    extract_text_from_pdf,
    extract_resume_with_llm,
    build_structured_resume
)

# ✅ Mock LLM JSON-like response (mimics Together API output)
mock_llm_api_output = {
    "choices": [{
        "text": json.dumps({
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone_number": "(123) 456-7890",
            "links": {
                "linkedin": "linkedin.com/in/janesmith",
                "github": "github.com/janesmith"
            },
            "summary": "Experienced software engineer...",
            "skills": {
                "technical_skills": ["Python", "Django"],
                "soft_skills": ["Teamwork", "Problem Solving"]
            },
            "education": [
                {"degree": "B.Sc. in CS", "institution": "XYZ University", "year": "2018"}
            ],
            "work_experience": [
                {"company": "TechCorp", "position": "Software Engineer", "duration": "2020 - Present"}
            ],
            "certifications": [],
            "projects": [],
            "languages": ["English"]
        })
    }]
}

# 🔍 Dynamically locate any resume in src/files/
def get_any_pdf_file():
    files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'files'))
    pdfs = glob(os.path.join(files_dir, '*.pdf'))
    if not pdfs:
        raise FileNotFoundError("❌ No PDF files found in src/files/")
    return os.path.basename(pdfs[0])

# 🧪 Test using a mocked TogetherResumeParser call
@patch("src.api.together_client_resume.TogetherResumeParser.extract_resume_data", return_value=mock_llm_api_output)
def test_llm_resume_parser(mock_extract_resume_data):
    filename = get_any_pdf_file()
    text = extract_text_from_pdf(filename)

    result = extract_resume_with_llm(text)
    structured = build_structured_resume(result)

    # ✅ Assertions
    assert isinstance(structured, dict)
    assert "skills" in structured
    assert "education" in structured
    assert "full_name" in structured
    assert structured["full_name"] == "Jane Smith"

    print("✅ Parsed Structured Resume (Mocked LLM):")
    print(json.dumps(structured, indent=2))
