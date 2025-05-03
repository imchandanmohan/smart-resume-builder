# src/extractors/jd_llm_extractor.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.extractors.extractor_fusion import BaseExtractor
from config.paths_config import *

class JDLLMExtractor(BaseExtractor):
    def extract(self):
        # 1. Define the JSON schema separately (no f-string here at all)
        json_schema = """
{
  "job_details": {
    "job_id": "",
    "job_title": "",
    "company_name": "",
    "location": "",
    "employment_type": "",
    "remote_or_onsite": "",
    "posted_date": "",
    "salary_range": "",
    "job_description": "",
    "responsibilities": [],
    "qualifications": [],
    "skills_required": [],
    "experience_level": "",
    "industry": "",
    "benefits": [],
    "company_website": "",
    "application_link": "",
    "recruiter_name": "",
    "recruiter_email": "",
    "visa_sponsorship": "",
    "deadline_to_apply": "",
    "interview_process": "",
    "tools_and_technologies": [],
    "language_requirements": [],
    "education_required": "",
    "notes": ""
  },
  "company_summary": {
    "summary": "",
    "writing_style": "",
    "candidate_expectations": "",
    "resume_tone": ""
  },
  "hidden_patterns_analysis": {
    "action_verbs_frequency": [],
    "metric_and_quantification_presence": "",
    "skill_grouping_patterns": [],
    "seniority_language_detected": "",
    "industry_keywords_detected": [],
    "soft_skills_detected": [],
    "problem_types_mentioned": [],
    "certifications_or_education_emphasis": "",
    "future_vision_language_detected": "",
    "tone_indicator": ""
  },
  "mandatory_candidate_qualities": [
    "", "", "", "", ""
  ],
  "top_keywords_for_ATS": [
    "", "", "", "", ""
  ],
  "example_resume_bullets": [
    "", ""
  ]
}
"""

        # 2. Now build the prompt
        prompt = (
            "# SYSTEM MESSAGE for GPT-4o\n"
            "# Purpose: JD Analyzer and Resume Strategy Generator\n\n"

            "You are an expert Job Description (JD) Analyzer and Resume Strategy Generator.\n\n"

            "Your task is:\n"
            "- Carefully read the provided Job Description (JD) and company details.\n"
            "- Deeply analyze the text to extract structured insights.\n"
            "- Output ONLY a strictly valid JSON object matching the schema provided below.\n\n"

            "Strict Instructions:\n"
            "- Return ONLY the pure JSON object, with no extra commentary, no headings, and no explanations.\n"
            "- If any field is missing in the JD, fill it with an empty string \"\" or empty list [].\n"
            "- Do not modify the structure or keys.\n"
            "- Do not invent information beyond what is reasonably inferred from the JD.\n"
            "- Stay concise inside the JSON fields.\n\n"

            "Focus Areas for Analysis:\n"
            "- Job details, company summary, candidate expectations\n"
            "- Hidden action verbs, skills, leadership cues, tone of writing\n"
            "- Extract mandatory candidate qualities\n"
            "- Detect top keywords for ATS (Applicant Tracking Systems)\n"
            "- Suggest 2 realistic example resume bullet points matching the JD tone\n\n"

            "Follow this JSON structure exactly:\n\n"
            f"{json_schema}\n\n"

            "---\n"
            "Below is the Job Description text for analysis:\n"
            "---\n"
            f"{self.text}\n"
            "---\n"
        )

        self.extract_with_llm(
            prompt=prompt,
            model_name="gpt-4o",
            vendor="openai"
        )


if __name__ == "__main__":
    extractor = JDLLMExtractor(
        txt_path=JOB_DESCRIPTION_PATH,
        output_path=PROCESSED_JOB_DESCRIPTION_PATH
    )
    extractor.extract()
