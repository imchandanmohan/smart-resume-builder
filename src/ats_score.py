import os
import sys
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.custom_exception import CustomException
from src.logger import get_logger
from config.paths_config import *


# Load .env and initialize client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise CustomException("OPENAI_API_KEY not found in environment variables", sys)

client = OpenAI(api_key=api_key)
logger = get_logger(__name__)


class ATSResumeAnalyzer:
    def __init__(self, resume_path: str = PROCESSED_RESUME_TEXT_FILE_PATH, jd_path: str = JOB_DESCRIPTION_PATH):
        self.resume_path = resume_path
        self.jd_path = jd_path
        self.max_retries = 1

    def _read_file(self, file_path: str) -> str:
        try:
            logger.info(f"Reading file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                logger.info(f"Read {len(content)} characters from {file_path}.")
                return content
        except Exception as e:
            logger.error(f"File read failed: {e}")
            raise CustomException(f"Failed to read file at {file_path}: {e}", sys)

    def _build_prompt(self, resume: str, jd: str) -> str:
        logger.info("Building prompt for OpenAI.")
        return f"""
You are an ATS resume analyzer. I will provide you with my resume and a job description.

Your task is to:
1. Evaluate my resume against the job description.
2. Score it based on ATS compatibility (out of 100) Remember to evaluate the score too strictly don't give free scores like 85% easily.
3. Check the resume strictly against the following grammar-based ATS resume rules:

✅ Grammar-Based ATS Resume Rules
- Start every bullet point with an action verb.
- Use present tense for current roles (e.g., "Lead", "Manage").
- Use past tense (-ed) for previous roles (e.g., "Led", "Managed").
- Follow action verbs with a clear impact statement.
- Include specific hard skills and platform-based skills throughout the experience section.
- Use quantifiable impact metrics (numbers, percentages) to show measurable achievements.
- Insert metrics either immediately after the action verb or after the impact statement.
- Write concise, one-line bullet points—avoid conjunctions and run-on sentences.
- Avoid using pronouns ("I", "my", "we") in any bullet point.
- Do not use complete paragraphs; only use bullet points for experience.
- Keep verb tense consistent within each role based on whether it is current or past.
- List education details (degree, school, GPA if >3.5, honors) in sentence fragments—no full sentences.
- Only include soft skills (e.g., communication, leadership) when demonstrated through action or results—not as generic claims.
- Avoid vague language (e.g., “responsible for”, “helped with”, “worked on”).
- Use specific industry-relevant terminology to align with job description keywords.
- Avoid filler words (e.g., "very", "really", "some", "a lot", "various").
- Never use question marks or exclamation points.
- Use consistent verb voice (active, not passive).
- Use parallel sentence structure for bullet points across similar roles.
- Always include a line like the following at the bottom or in the summary/header:
- Limit to 10 high-impact suggestions maximum.
- Only give suggestions if they are genuinely needed — do not invent issues if the resume meets all criteria.
Below is my resume and job description
---

📄 **Resume**  
{resume}

📑 **Job Description**  
{jd}

---

Return the output **only** in the following **JSON format**:

{{
  "ATS_score": <score>,
  "issues": {{
    "Searchability": <int>,
    "Hard Skills": <int>,
    "Soft Skills": <int>,
    "Recruiter Tips": <int>,
    "Formatting": <int>
  }},
  "suggestions": [
    {{"text": "<description of issue or improvement>", "category": "error" | "warning" | "suggestion" | "information"}}
  ]
}}
"""


    def _call_openai(self, prompt: str) -> str:
        logger.info("Calling OpenAI API...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            content = response.choices[0].message.content

            # Clean response if wrapped in markdown
            if content.startswith("```json"):
                content = content.lstrip("```json").rstrip("```").strip()
            elif content.startswith("```"):
                content = content.lstrip("```").rstrip("```").strip()

            logger.info("Received response from OpenAI.")
            return content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise CustomException(f"OpenAI API call failed: {e}", sys)

    def _validate_and_parse(self, response: str, original_prompt: str, retry_count: int = 0):
        try:
            logger.info("Parsing OpenAI response...")
            result = json.loads(response)
            if "ATS_score" not in result or "suggestions" not in result:
                raise ValueError("Missing required keys.")
            logger.info("Response parsed successfully.")
            return result
        except Exception as e:
            logger.warning(f"Response parse failed: {e}")
            if retry_count < self.max_retries:
                logger.warning("Retrying OpenAI call due to invalid format...")
                time.sleep(2)
                retry_response = self._call_openai(original_prompt)
                return self._validate_and_parse(retry_response, original_prompt, retry_count + 1)
            else:
                raise CustomException(f"Failed to parse OpenAI response after retry: {e}", sys)

    def analyze(self):
        try:
            resume_text = self._read_file(self.resume_path)
            jd_text = self._read_file(self.jd_path)
            prompt = self._build_prompt(resume_text, jd_text)

            raw_response = self._call_openai(prompt)
            result = self._validate_and_parse(raw_response, prompt)
            return result
        except Exception as e:
            raise CustomException(f"ATS analysis failed: {e}", sys)


if __name__ == "__main__":
    try:
        print("🚀 Starting ATS resume analysis...")
        analyzer = ATSResumeAnalyzer()
        output = analyzer.analyze()
        print("\n✅ Final Output:\n")
        print(json.dumps(output, indent=2))
    except Exception as err:
        logger.error(f"Execution failed: {err}")
        print(f"❌ Error: {err}")
