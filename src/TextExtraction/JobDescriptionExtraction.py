import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import re
import time
import string
from typing import Dict, List
from src.api.together_client import query_together_ai

class JobDescriptionParser:
    # =================== Utilities ===================
    def truncate_text(self, text: str, max_tokens: int = 500) -> str:
        words = text.split()
        return " ".join(words[:max_tokens]) if len(words) > max_tokens else text

    def clean_response(self, response: str) -> List[str]:
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        cleaned = [re.sub(r"^[\-\*\•]+\s*", "", line).strip() for line in lines if len(line) > 3]
        return [re.sub(r"\s+", " ", line) for line in cleaned]



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
    
    def normalize_keywords(self, keywords: List[str]) -> List[str]:
        return list({
        kw.strip().strip(string.punctuation).capitalize()
        for kw in keywords if kw.strip()
        })


    # =================== Extraction Functions ===================
    def extract_job_title(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(query_together_ai("Extract only the job title:\n\n" + text))

    def extract_company_name(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(query_together_ai("Extract the company name only, with no prefixes like 'Company:'. Respond with the clean name only:\n\n" + text))

    def extract_location(self, text: str) -> str:
        time.sleep(6)
        return self.deduplicate_text(query_together_ai("Extract only the job location:\n\n" + text))

    def extract_responsibilities(self, text: str) -> List[str]:
        time.sleep(6)
        raw = query_together_ai("Extract only the job responsibilities (avoid qualifications, skills, or benefits)..." + text)
        return self.deduplicate_list(self.clean_response(raw))

    def extract_technical_skills(self, text: str) -> List[str]:
        time.sleep(6)
        response = query_together_ai("Extract only technical or hard skills mentioned in the job description (e.g., Python, SQL, data modeling). ""Do NOT include years of experience, degrees, education levels, or certifications. ""Return as a comma-separated list:\n\n" + text)
        items = [s.strip() for s in response.split(",") if s.strip()]
        seen, deduped = set(), []
        for it in items:
            low = it.lower()
            if low not in seen:
                seen.add(low)
                deduped.append(it)
        return deduped

    
    def extract_soft_skills(self, text: str) -> List[str]:
        time.sleep(6)
        response = query_together_ai( "Extract only soft skills or interpersonal skills mentioned in the job description (e.g., communication, leadership, problem-solving). ""Exclude technical skills and tools. Return as a comma-separated list:\n\n" + text )
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
        raw = query_together_ai("Extract only formal qualifications like degrees, certifications, and education level. ""Do not include work experience. Respond as bullet points:\n\n" + text)
        return self.deduplicate_list(self.clean_response(raw))

    def extract_experience(self, text: str) -> List[str]:
        time.sleep(6)
        raw = query_together_ai("Extract only experience requirements from the job description. ""This includes years of experience, relevant job titles, seniority level, and domain-specific work experience. ""Do not include degrees, certifications, skills, or headers. ""Respond only as bullet points:\n\n" + text)
        cleaned = self.clean_response(raw)
        filtered = [line for line in cleaned if not line.lower().startswith("experience requirements:")]
        return self.deduplicate_list(filtered)


    def extract_keywords(self, text: str) -> List[str]:
        time.sleep(6)
        raw = query_together_ai("Extract the top 10 keywords or skills relevant to the role as a comma-separated list:\n\n" + text)
        items = [k.strip() for k in raw.split(",") if k.strip()]
        return self.normalize_keywords(items)


    def extract_benefits(self, text: str) -> List[str]:
        time.sleep(6)
        raw = query_together_ai("Extract only the benefits and perks offered in the job. List them as bullet points:\n\n" + text)
        return self.deduplicate_list(self.clean_response(raw))

    def extract_job_type(self, text: str) -> str:
        time.sleep(6)
        raw = query_together_ai("Extract only the job type (e.g. Full-time, Part-time, Contract, Internship). ""Do not include labels like 'Job Type:'. Respond with a single phrase only:\n\n" + text)
        return self.deduplicate_text(raw)

    def parse(self, text: str) -> dict:
        return {
            "job_title": self.extract_job_title(text),
            "company_name": self.extract_company_name(text),
            "location": self.extract_location(text),
            "responsibilities": self.extract_responsibilities(text),
            "technical_skills": self.extract_technical_skills(text),
            "soft_skills": self.extract_soft_skills(text),
            "qualifications": self.extract_qualifications(text),
            "experience": self.extract_experience(text),
            "keywords": self.extract_keywords(text),
            "benefits": self.extract_benefits(text),
            "job_type": self.extract_job_type(text),
        }

