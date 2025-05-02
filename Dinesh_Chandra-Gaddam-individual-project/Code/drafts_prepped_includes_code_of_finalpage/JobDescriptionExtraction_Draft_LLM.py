import os
import re
import time
import requests
from typing import Dict, List
from dotenv import load_dotenv

class JobDescriptionParser:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        # =================== Config ===================
        self.TOGETHER_KEY = os.getenv("TOGETHER_API_KEY")
        if not self.TOGETHER_KEY:
            raise ValueError("TOGETHER_API_KEY not found in .env file")
        self.TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    # =================== Utilities ===================
    def truncate_text(self, text: str, max_tokens: int = 500) -> str:
        words = text.split()
        return " ".join(words[:max_tokens]) if len(words) > max_tokens else text

    def clean_response(self, response: str) -> List[str]:
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        return [re.sub(r"\s+", " ", line) for line in lines if len(line) > 5]

    def deduplicate_text(self, text: str) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        seen = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in seen:
                seen.append(sentence)
        return ' '.join(seen)

    def deduplicate_list(self, lst: List[str]) -> List[str]:
        seen = []
        for item in lst:
            if item not in seen:
                seen.append(item)
        return seen

    # =================== Together AI Query ===================
    def query_together_ai(self, prompt: str) -> str:
        system_message = (
            "You are an expert at extracting structured information from job descriptions. "
            "Return only the requested info in plain text with no extra commentary."
        )
        full_prompt = f"{system_message}\n\n{prompt}"
        trimmed_prompt = self.truncate_text(full_prompt)

        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.TOGETHER_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.TOGETHER_MODEL,
            "messages": [{"role": "user", "content": trimmed_prompt}],
            "temperature": 0.0
        }

        retries = 3
        for attempt in range(retries):
            try:
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 429:
                    print("⚠️ Rate limit hit. Waiting 60 seconds before retrying...")
                    time.sleep(60)
                    continue
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                print(f"❌ Error querying Together AI: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    return "Error processing the request."

    # =================== Extraction Functions ===================
    def extract_job_title(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(self.query_together_ai("Extract only the job title:\n\n" + text))

    def extract_company_name(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(self.query_together_ai("Extract only the company name:\n\n" + text))

    def extract_location(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(self.query_together_ai("Extract only the job location:\n\n" + text))

    def extract_responsibilities(self, text: str) -> List[str]:
        time.sleep(6)
        return self.deduplicate_list(self.clean_response(self.query_together_ai("Extract the responsibilities as bullet points:\n\n" + text)))

    def extract_required_skills(self, text: str) -> List[str]:
        time.sleep(6)
        response = self.query_together_ai("Extract required skills as a comma-separated list:\n\n" + text)
        items = [s.strip() for s in response.split(",") if s.strip()]
        seen, deduped = set(), []
        for it in items:
            low = it.lower()
            if low not in seen:
                seen.add(low)
                deduped.append(it)
        return deduped

    def extract_qualifications(self, text: str) -> List[str]:
        time.sleep(6)
        return self.deduplicate_list(self.clean_response(self.query_together_ai("Extract the qualifications as bullet points:\n\n" + text)))

    def extract_experience(self, text: str) -> List[str]:
        time.sleep(6)
        return self.deduplicate_list(self.clean_response(self.query_together_ai("Extract the experience as bullet points:\n\n" + text)))

    def extract_keywords(self, text: str) -> List[str]:
        time.sleep(6)
        response = self.query_together_ai("Extract top 10 keywords as a comma-separated list:\n\n" + text)
        items = [k.strip() for k in response.split(",") if k.strip()]
        seen, deduped = set(), []
        for kw in items:
            low = kw.lower()
            if low not in seen:
                seen.add(low)
                deduped.append(kw)
        return deduped

    def extract_benefits(self, text: str) -> List[str]:
        time.sleep(6)
        return self.deduplicate_list(self.clean_response(self.query_together_ai("Extract the benefits as bullet points:\n\n" + text)))

    def extract_job_type(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(self.query_together_ai("Extract the job type (Full-time, Part-time, etc.):\n\n" + text))

    def extract_ats_score(self, text: str) -> Dict[str, float]:
        time.sleep(6)
        response = self.query_together_ai("Provide keyword_density, formatting_score, section_score as comma-separated numeric values:\n\n" + text)
        parts = [x.strip() for x in response.split(",") if x.strip()]
        if len(parts) != 3:
            return {"keyword_density": 0.0, "formatting_score": 0.0, "section_score": 0.0}
        try:
            vals = [float(x) for x in parts]
            return {
                "keyword_density": vals[0],
                "formatting_score": vals[1],
                "section_score": vals[2]
            }

        except:
            return {"keyword_density": 0.0, "formatting_score": 0.0, "section_score": 0.0}

    def parse(self, text: str) -> dict:
        return {
            "job_title": self.extract_job_title(text),
            "company_name": self.extract_company_name(text),
            "location": self.extract_location(text),
            "responsibilities": self.extract_responsibilities(text),
            "skills": self.extract_required_skills(text),
            "qualifications": self.extract_qualifications(text),
            "experience": self.extract_experience(text),
            "keywords": self.extract_keywords(text),
            "benefits": self.extract_benefits(text),
            "job_type": self.extract_job_type(text),
            "ats_score": self.extract_ats_score(text)
        }