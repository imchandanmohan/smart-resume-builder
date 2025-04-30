# src/extractors/resume_llm_extractor.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.extractors.extractor_fusion import BaseExtractor
from config.paths_config import *

# your ResumeLLMExtractor code...

class ResumeLLMExtractor(BaseExtractor):
    def extract(self):
        json_schema = """
        {
          "full_name": "",
          "email": "",
          "phone_number": "",
          "linkedin_url": "",
          "portfolio_url": "",
          "location": "",
          "summary": "",
          "skills": [],
          "education": [
            {
              "degree": "",
              "field_of_study": "",
              "school_name": "",
              "start_date": "",
              "end_date": "",
              "grade_or_gpa": "",
              "description": ""
            }
          ],
          "work_experience": [
            {
              "job_title": "",
              "company_name": "",
              "location": "",
              "start_date": "",
              "end_date": "",
              "responsibilities": []
            }
          ],
          "certifications": [
            {
              "name": "",
              "organization": "",
              "date_obtained": ""
            }
          ],
          "languages": [],
          "projects": [
            {
              "project_name": "",
              "description": "",
              "technologies_used": []
            }
          ],
          "awards": [],
          "publications": [],
          "volunteer_experience": [
            {
              "role": "",
              "organization": "",
              "description": "",
              "start_date": "",
              "end_date": ""
            }
          ],
          "notes": "",
          "candidate_summary": "",
          "core_skills_and_technologies": [],
          "work_experience_summary": [],
          "education_summary": [],
          "certifications_summary": [],
          "languages_known": [],
          "soft_skills_detected": [],
          "resume_writing_style": "",
          "strengths_detected": [],
          "areas_for_improvement": [],
          "overall_resume_impression": ""
        }
        """

        instructions = f"""
        You are an expert Resume Extractor and Analyzer.

        Tasks:
        - Carefully read the provided resume text.
        - Extract structured information according to the schema below.
        - **Responsibilities** must be extracted as bullet point arrays.
        - **Projects' description** must be extracted as bullet point arrays.
        - **Education** must include a "description" field if there are any activities, projects, or research mentioned during studies. Leave empty if not found.

        In addition:
        - For fields like `summary`, `candidate_summary`, `core_skills_and_technologies`, `work_experience_summary`, `education_summary`, `certifications_summary`, `languages_known`, `soft_skills_detected`, `resume_writing_style`, `strengths_detected`, `areas_for_improvement`, and `overall_resume_impression`, **analyze** the resume and **generate concise professional content** based on your understanding.
        - Missing information must be an empty string "" or empty list [].
        - Do not change the user's text when extracting direct responsibilities and project descriptions.
        - Output **only a valid JSON object**, no extra text or explanation.

        JSON Schema:
        {json_schema}

        ---

        Resume Text:
        \"\"\"
        {self.text}
        \"\"\"

        ONLY return valid JSON.
        """



        self.extract_with_llm(
            prompt=instructions,
            model_name="gpt-4o",
            vendor="openai"
        )

if __name__ == "__main__":
    extractor = ResumeLLMExtractor(
        txt_path=PROCESSED_RESUME_TEXT_FILE_PATH,
        output_path=PROCESSED_RESUME_JSON_FILE_PATH
    )
    extractor.extract()
