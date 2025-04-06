import os
import requests

class TogetherResumeParser:
    def __init__(self, api_key=None, model="mistralai/Mixtral-8x7B-Instruct-v0.1"):
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.model = model
        self.url = "https://api.together.xyz/inference"

    def extract_resume_data(self, resume_text):
        prompt = self._build_prompt(resume_text)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 2048,
            "temperature": 0.3,
            "top_p": 0.9
        }

        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Depending on Together.ai response format:
        return result.get("output", result)

    def _build_prompt(self, resume_text):
        return f"""
You are a resume parser. Extract the following details from this resume in clean, structured JSON format:

- Full Name
- Email
- Phone Number
- LinkedIn / GitHub / Portfolio URLs
- Summary
- Skills (separate into technical_skills and soft_skills)
- Education (degree, institution, year)
- Work Experience (title, company, duration, responsibilities)
- Certifications
- Projects
- Languages

Return only valid JSON.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
