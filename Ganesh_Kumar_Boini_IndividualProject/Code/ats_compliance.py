# modules/analysis/ats_compliance.py

import re
import json
from typing import Dict, Union, List, Optional
from modules.analysis.score_component import ScoreComponent
from NER.ner_service import NERService

class ATSComplianceChecker:
    """
    ATS‐friendly structure & keyword check, now loading
    skills_required from data/job_description.json internally.
    """

    def __init__(
        self,
        resume_text: str,
        job_description_text: Optional[str] = None,
        file_extension: str = ".pdf",
        jd_json_path: str = "data/job_description.json"
    ):
        self.text           = resume_text
        self.jd_text        = job_description_text or ""
        self.file_extension = file_extension.lower()

        # load JD JSON and extract required skills
        try:
            jd_data = json.load(open(jd_json_path))
            jd_details = jd_data.get("job_details", jd_data)
            self.jd_required = [s.lower() for s in jd_details.get("skills_required", [])]
            # optional: also pull HARD skills from the 'qualifications' via NER
            self.ner = NERService()
            self.jd_preferred = []
            for phrase in jd_details.get("qualifications", []):
                ents = self.ner.predict(phrase).get("entities", [])
                for ent in ents:
                    if ent["label"] == "HARD":
                        self.jd_preferred.append(ent["text"].lower())
        except Exception:
            # fallback: no JD JSON found
            self.jd_required = []
            self.jd_preferred = []
            self.ner = NERService()

        # internal state
        self.issues             : List[str] = []
        self.section_scores     : Dict[str,int] = {}
        self.contact_penalty    = 0
        self.formatting_penalty = 0
        self.content_penalty    = 0
        self.jd_penalty         = 0

        lines = [l.strip() for l in self.text.splitlines() if l.strip()]
        self.lines      = lines
        self.top_text   = " ".join(lines[: max(1, len(lines)//5)]).lower()
        self.text_lower = self.text.lower()

    def check_sections(self):
        SECTION_SYNONYMS = {
            "education":  ["education", "academic background"],
            "experience": ["experience", "work history", "employment"],
            "skills":     ["skills", "technical skills", "tech stack"],
            "projects":   ["projects", "personal projects", "side projects"]
        }
        for sec, alts in SECTION_SYNONYMS.items():
            if any(re.search(rf'(?i)\b{alt}\b', self.text) for alt in alts):
                self.section_scores[sec] = 1
            else:
                self.section_scores[sec] = 0
                self.formatting_penalty  -= 10
                self.issues.append(f"❌ Missing section: **{sec.title()}**")

    def check_contact_info(self):
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w{2,}\b', self.top_text):
            self.contact_penalty   -= 10
            self.issues.append("❌ Missing **email** near top")
        if not re.search(r'\b\d{10}\b|\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', self.top_text):
            self.contact_penalty   -= 5
            self.issues.append("❌ Missing **phone** near top")
        if "linkedin" not in self.top_text:
            self.contact_penalty   -= 5
            self.issues.append("❌ Missing **LinkedIn** near top")
        # Use NER to find a GPE/LOC or accept "remote"
        ents = self.ner.predict(self.top_text).get("entities", [])
        if not any(e["label"] in {"GPE", "LOC"} for e in ents) and "remote" not in self.top_text:
            self.contact_penalty   -= 5
            self.issues.append("❌ Missing **location/Remote** near top")

    def check_formatting(self):
        if not re.search(r'^(\-|\*|\•|\d+\.)\s', self.text, re.MULTILINE):
            self.formatting_penalty -= 5
            self.issues.append("❌ No **bullet points** found")
        if re.search(r'\+\-+\+|\|', self.text):
            self.formatting_penalty -= 10
            self.issues.append("❌ Detected **tables or complex layout**")
        if re.search(r'[\u25A0-\u25FF\u2600-\u26FF]', self.text):
            self.formatting_penalty -= 5
            self.issues.append("❌ Detected **icons or symbols**")
        if any(len(l) > 120 for l in self.lines):
            self.formatting_penalty -= 3
            self.issues.append("⚠️ Some **lines exceed 120 chars**")
        if len(max(self.lines, key=len, default="")) > 150:
            self.formatting_penalty -= 2
            self.issues.append("⚠️ Very long line detected — consider splitting")

    def check_content_quality(self):
        passive = len(re.findall(r"\b(is|am|are|was|were)\s+\w+\s+by\b", self.text_lower))
        if passive:
            self.content_penalty -= 3
            self.issues.append(f"⚠️ Passive voice in {passive} sentence(s)")
        for ph in ["responsible for","hardworking","team player","go-getter","synergy","detail-oriented"]:
            if ph in self.text_lower:
                self.content_penalty -= 1
                self.issues.append(f"⚠️ Overused phrase: _{ph}_")

    def check_jd_keywords(self):
        # now only compare against required (and preferred) HARD skills
        if self.jd_required or self.jd_preferred:
            found_words = set(re.findall(r'\b\w[\w+-]*\b', self.text_lower))
            missing_req = set(self.jd_required) - found_words
            missing_pref= set(self.jd_preferred) - found_words
            # penalize required more heavily
            if missing_req:
                self.jd_penalty -= min(10, len(missing_req))
                sample = ", ".join(list(missing_req)[:3])
                self.issues.append(f"⚠️ Missing required skills: _{sample}_")
            if missing_pref:
                self.jd_penalty -= min(5, len(missing_pref))
                sample = ", ".join(list(missing_pref)[:3])
                self.issues.append(f"⚠️ Missing preferred quals: _{sample}_")

    def bonus_action_verbs(self) -> int:
        hits = len(re.findall(
            r'\b(designed|developed|led|improved|implemented|built|created|trained|enhanced|deployed|launched|automated)\b',
            self.text_lower
        ))
        return 5 if hits >= 5 else 0

    def evaluate(self) -> Dict[str, Union[int, List[str], Dict[str,int], ScoreComponent]]:
        # run all checks
        self.check_sections()
        self.check_contact_info()
        self.check_formatting()
        self.check_content_quality()
        self.check_jd_keywords()
        bonus = self.bonus_action_verbs()

        total_penalty = -(self.contact_penalty + self.formatting_penalty +
                          self.content_penalty + self.jd_penalty)
        base_pts  = 25
        raw_pts   = max(0, base_pts - total_penalty + bonus)
        raw_pct   = round(raw_pts / base_pts * 100, 2)
        score     = round(raw_pct * (5 / 100), 2)  # out of 5

        notes = []
        if self.contact_penalty < 0:
            notes.append(f"Contact issues: {abs(self.contact_penalty)}pt penalty")
        if self.formatting_penalty < 0:
            notes.append(f"Formatting issues: {abs(self.formatting_penalty)}pt penalty")
        if self.content_penalty < 0:
            notes.append(f"Content issues: {abs(self.content_penalty)}pt penalty")
        if self.jd_penalty < 0:
            notes.append(f"JD skill gaps: {abs(self.jd_penalty)}pt penalty")
        if bonus:
            notes.append(f"Action-verb bonus: +{bonus}pt")

        component = ScoreComponent(
            name="ATS Compliance",
            weight=5,
            raw=raw_pct,
            score=score,
            notes=notes or ["No major compliance issues"]
        )

        return {
            "component": component,
            "issues": self.issues,
            "section_scores": self.section_scores,
            "contact_penalty": self.contact_penalty,
            "formatting_penalty": self.formatting_penalty,
            "content_penalty": self.content_penalty,
            "jd_penalty": self.jd_penalty,
            "bonus_action_verbs": bonus
        }
