# %%
import re
import spacy
from collections import Counter
from typing import Dict, List, Union
from transformers import pipeline
from sentence_transformers import SentenceTransformer


class JobDescriptionParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_trf")  # Transformer-based NER
        self.qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")  # LLM for QA
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Contextual embeddings for job title recognition

    def parse(self, job_text: str) -> Dict[str, Union[List[str], str, Dict[str, float]]]:
        return {
            "job_title": self.extract_job_title(job_text),
            "company_name": self.extract_company_name(job_text),
            "location": self.extract_location(job_text),
            "responsibilities": self.extract_responsibilities(job_text),
            "skills": self.extract_required_skills(job_text),
            "qualifications": self.extract_qualifications(job_text),
            "experience": self.extract_experience(job_text),
            "keywords": self.extract_keywords(job_text),
            "benefits": self.extract_benefits(job_text),
            "job_type": self.extract_job_type(job_text),
            "ats_score": self.ats_optimization_score(job_text)
        }

    def preprocess_text(self, text: str) -> str:
        """
        Clean up and normalize the text to prepare for parsing.
        """
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    def extract_section_items(self, text: str, section_header_regex: str) -> List[str]:
        """
        Generic method to extract bullet point items under a specific section header.
        """
        lines = text.split("\n")
        section_items = []
        in_section = False

        for line in lines:
            if re.search(section_header_regex, line, re.IGNORECASE):
                in_section = True
                continue

            if in_section:
                # Stop if we hit another section or a blank line
                if re.match(r"^[A-Z][a-z]+:", line.strip()) or line.strip() == "":
                    break
                cleaned_line = line.strip("-• \t").strip()
                if cleaned_line:
                    section_items.append(cleaned_line)

        return section_items

    def extract_job_title(self, text: str) -> str:
        match = re.search(
            r'(Job Title[:\s]*)([A-Za-z\s]+)',
            text,
            re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return ""

    def extract_company_name(self, text: str) -> str:
        """
        Extract company name using NER or regex fallback.
                """
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text.strip()

        # Fallback: Look for common phrases
        match = re.search(r"(?:at|with|by|for|join)\s+([A-Z][A-Za-z0-9\s&.,]+)", text)
        if match:
            return match.group(1).strip()

        # Consider "Company:" pattern
        match = re.search(r"Company[:\s]*([A-Z][A-Za-z0-9\s&.,]+)", text)
        return match.group(1).strip() if match else ""

    def extract_location(self, text: str) -> str:
        """
        Extract geographic location using spaCy's NER with regex fallback.
                """
        doc = self.nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

        if locations:
            return ", ".join(set(locations))

        # Fallback: Look for common location phrases
        match = re.search(r"(?:Location|Based in|Work Location|Located at)[:\s]*([A-Za-z0-9,\s]+)", text)
        return match.group(1).strip() if match else ""

    def extract_responsibilities(self, text: str) -> List[str]:
        lines = text.split('\n')
        responsibilities = []
        in_responsibility_section = False
        for line in lines:
            if re.search(r"responsibilit(y|ies)", line, re.IGNORECASE):
                in_responsibility_section = True
            elif in_responsibility_section and line.strip() == "":
                break
            elif in_responsibility_section:
                responsibilities.append(line.strip("- ").strip())
        return responsibilities

    def extract_required_skills(self, text: str) -> List[str]:
        skill_keywords = [
            "Python",
            "Java",
            "SQL",
            "communication",
            "teamwork",
            "leadership"
        ]
        found_skills = [skill for skill in skill_keywords if re.search(fr"\b{skill}\b", text, re.IGNORECASE)]
        return found_skills

    def extract_qualifications(self, text: str) -> List[str]:
        qualifications = []
        pattern = re.compile(r"(Bachelor's|Master's|PhD|MBA|degree|certification|diploma|license)", re.IGNORECASE)
        lines = text.split("\n")
        for line in lines:
            if pattern.search(line):
                qualifications.append(line.strip())
        return qualifications

    def extract_experience(self, text: str) -> List[str]:
        pattern = re.compile(r'(\d+\+?\s*(years|yrs)\s+of\s+experience)', re.IGNORECASE)
        return [match.group() for match in pattern.finditer(text)]

    def extract_keywords(self, text: str) -> List[str]:
        doc = self.nlp(text.lower())
        words = [token.text for token in doc if token.is_alpha and not token.is_stop]
        freq = Counter(words)
        return [word for word, count in freq.most_common(10)]

    def extract_benefits(self, text: str) -> List[str]:
        benefits_keywords = ["health insurance", "401k", "paid time off", "remote work", "bonus", "stock options"]
        found = [b for b in benefits_keywords if b in text.lower()]
        return found

    def extract_job_type(self, text: str) -> str:
        """
        Dynamically detects job type from description.
        """
        job_types = [
            "full-time", "part-time", "contract", "temporary",
            "internship", "freelance", "hybrid", "remote"
        ]
        for jt in job_types:
            if re.search(jt, text, re.IGNORECASE):
                print(jt)
                return jt
        return ""

    def ats_optimization_score(self, text: str) -> Dict[str, float]:
        doc = self.nlp(text.lower())
        words = [token.text for token in doc if token.is_alpha]
        unique_words = set(words)
        keyword_density = len(unique_words) / max(len(words), 1)
        formatting_score = 1.0 if "responsibilities" in text.lower() and "qualifications" in text.lower() else 0.5
        return {
            "keyword_density": round(keyword_density, 2),
            "formatting_score": formatting_score
        }
    
