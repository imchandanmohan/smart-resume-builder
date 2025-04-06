import json
import re
import sys
import os
import pdfplumber


# Add the root directory to the Python path (one level up from src)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.api.together_client_resume import TogetherResumeParser

# 🧱 Extract raw text from a PDF file
def extract_text_from_pdf(filename):
    files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../files"))
    file_path = os.path.join(files_dir, filename)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Resume not found: {file_path}")

    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text.strip()


# 🧠 Send resume text to Together.ai and extract JSON
def extract_resume_with_llm(text):
    parser = TogetherResumeParser()
    response = parser.extract_resume_data(text)

    try:
        llm_text = response['choices'][0]['text'].strip()

        # Try to extract JSON inside code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", llm_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            match = re.search(r"(\{.*\})", llm_text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                raise ValueError("No JSON content found in LLM response.")

        return json.loads(json_str)

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        print("❌ Failed to extract structured resume from Together.ai output.")
        print("Raw LLM response:\n", llm_text)
        raise e


# 🧱 Build a default-safe resume dictionary
def build_structured_resume(parsed):
    return {
        "full_name": parsed.get("full_name", None),
        "email": parsed.get("email", None),
        "phone_number": parsed.get("phone_number", None),
        "links": parsed.get("links") or parsed.get("urls") or {
            "linkedin": None,
            "github": None,
            "portfolio": None
        },
        "summary": parsed.get("summary", None),
        "skills": parsed.get("skills") or {
            "technical_skills": parsed.get("technical_skills", []),
            "soft_skills": parsed.get("soft_skills", [])
        },
        "education": parsed.get("education", []),
        "work_experience": parsed.get("work_experience", []),
        "certifications": parsed.get("certifications", []),
        "projects": parsed.get("projects", []),
        "languages": parsed.get("languages", [])
    }


# 📄 Pretty print
def print_structured_resume(resume_json):
    print("\n🧾 COMPLETE STRUCTURED RESUME JSON\n")
    print(json.dumps(resume_json, indent=2))



