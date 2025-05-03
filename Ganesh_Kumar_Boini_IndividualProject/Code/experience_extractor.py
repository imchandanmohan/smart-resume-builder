# modules/analysis/experience_extractor.py

import re
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from dateutil.relativedelta import relativedelta
import spacy

from modules.extraction.text_preprocessor import TextPreprocessor
from NER.ner_service import NERService
from modules.analysis.score_component import ScoreComponent  # ← import added

MONTH_FMT = "%b %Y"

class ExperienceExtractor:
    """
    Calculates an Experience Alignment score (E) out of 20, with:
      • 30% weight → total years (capped at full_score_years)
      • 20% weight → recency (any role ended within 2 years)
      • 40% weight → relevance (overlap of HARD skills between experience bullets and JD responsibilities)
    +5% bonus if leadership (“led … team”) via ACTION label
    +5% bonus if project depth (any HARD label) appears

    Uses TextPreprocessor to clean bullet text before NER-based checks.
    """

    def __init__(self, preprocessor: Optional[TextPreprocessor] = None):
        self.nlp = spacy.load("en_core_web_sm")
        self.tp  = preprocessor or TextPreprocessor()
        self.ner = NERService()

    def _parse_json_experiences(
        self, resume_json: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        now = datetime.now()
        experiences = []
        for entry in resume_json.get("work_experience", []):
            start_str = entry.get("start_date", "")
            end_str   = entry.get("end_date", "")
            try:
                start = datetime.strptime(start_str, MONTH_FMT)
            except Exception:
                continue
            if end_str.lower() == "present":
                end = now
            else:
                try:
                    end = datetime.strptime(end_str, MONTH_FMT)
                except Exception:
                    end = now
            experiences.append({
                "title": entry.get("job_title", ""),
                "start": start,
                "end": end,
                "responsibilities": entry.get("responsibilities", [])
            })
        return experiences

    def _parse_regex_experiences(
        self, resume_text: str
    ) -> List[Dict[str, Any]]:
        now = datetime.now()
        experiences = []
        pattern = re.compile(r"(\w{3}\s+\d{4})\s*[-–]\s*(Present|\w{3}\s+\d{4})", re.IGNORECASE)
        for match in pattern.finditer(resume_text):
            span_start = match.start()
            line_start = resume_text.rfind("\n", 0, span_start) + 1
            title = resume_text[line_start:span_start].strip()
            start_str, end_str = match.group(1), match.group(2)
            try:
                start = datetime.strptime(start_str, MONTH_FMT)
            except Exception:
                continue
            end = now if end_str.lower() == "present" else datetime.strptime(end_str, MONTH_FMT)
            experiences.append({
                "title": title,
                "start": start,
                "end": end,
                "responsibilities": []
            })
        return experiences

    def _fuzzy_title_match(self, jd_title: str, exp_title: str) -> bool:
        jd, ex = jd_title.lower(), exp_title.lower()
        return jd in ex or ex in jd

    def calculate_experience_alignment(
        self,
        resume_json: Optional[Dict[str, Any]] = None,
        resume_text: Optional[str] = None,
        jd_json: Optional[Dict[str, Any]] = None,
        jd_text: Optional[str] = None,
        full_score_years: int = 5
    ) -> Dict[str, Any]:
        now = datetime.now()

        # 1) Extract experiences from JSON or fallback regex
        if resume_json and resume_json.get("work_experience"):
            experiences = self._parse_json_experiences(resume_json)
        else:
            experiences = self._parse_regex_experiences(resume_text or "")

        # 2) Build bullets list
        bullets: List[str] = []
        for exp in experiences:
            bullets += exp.get("responsibilities", [])
        if not bullets and resume_text:
            bullets = [resume_text]

        # 3) Compute years of experience and recency
        total_years = 0.0
        has_recent  = False
        for exp in experiences:
            delta = relativedelta(exp["end"], exp["start"])
            total_years += delta.years + delta.months / 12.0
            if (now - exp["end"]).days <= 730:
                has_recent = True

        year_score   = min(total_years / full_score_years, 1.0)
        recent_score = 1.0 if has_recent else 0.0

        # 4) Compute relevance: overlap of HARD tokens between bullets & JD responsibilities
        jd_resps = jd_json.get("responsibilities", []) if jd_json else []
        if jd_text:
            jd_resps.append(jd_text)
        jd_hard: Set[str] = set()
        for text in jd_resps:
            for ent in self.ner.predict(text).get("entities", []):
                if ent["label"] == "HARD":
                    jd_hard.add(ent["text"].lower())

        relevance_score = 0.0
        if jd_hard:
            ratios = []
            for bullet in bullets:
                bullet_hard = {
                    ent["text"].lower()
                    for ent in self.ner.predict(bullet).get("entities", [])
                    if ent["label"] == "HARD"
                }
                ratios.append(len(bullet_hard & jd_hard) / len(jd_hard))
            relevance_score = sum(ratios) / len(ratios) if ratios else 0.0

        # 5) Base raw percentage (0–100)
        base_raw_pct = round(
            (0.3 * year_score + 0.2 * recent_score + 0.4 * relevance_score) * 100,
            2
        )

        # 6) Dynamic bonuses via NER
        leadership_bonus_pct = 0.0
        depth_bonus_pct      = 0.0

        for bullet in bullets:
            ents = self.ner.predict(bullet).get("entities", [])
            # Leadership: any ACTION label with lemma 'lead'
            for ent in ents:
                if ent["label"] == "ACTION" and self.nlp(ent["text"].lower())[0].lemma_ == "lead":
                    leadership_bonus_pct = 5.0
                    break
            # Depth: any HARD label
            if any(ent["label"] == "HARD" for ent in ents):
                depth_bonus_pct = 5.0
            if leadership_bonus_pct and depth_bonus_pct:
                break

        boosted_raw_pct = min(base_raw_pct + leadership_bonus_pct + depth_bonus_pct, 100.0)
        final_score     = round(boosted_raw_pct / 100 * 20, 2)

        # ── 7) Build ScoreComponent ─────────────────────────────
        notes = [
            f"Years of exp   : {round(total_years,2)} ({year_score*100:.0f}% of target)",
            f"Recent role    : {'Yes' if has_recent else 'No'}",
            f"Relevance      : {relevance_score*100:.0f}%",
        ]
        if leadership_bonus_pct:
            notes.append(f"Leadership +{int(leadership_bonus_pct)}%")
        if depth_bonus_pct:
            notes.append(f"Depth +{int(depth_bonus_pct)}%")

        component = ScoreComponent(
            name="Experience Alignment",
            weight=20,
            raw=boosted_raw_pct,
            score=final_score,
            notes=notes
        )

        # ── 8) Return complete results ───────────────────────────
        return {
            "years_of_experience": round(total_years, 2),
            "year_score": round(year_score, 2),
            "recent_experience_score": recent_score,
            "relevance_score": round(relevance_score, 2),
            "base_raw_pct": base_raw_pct,
            "leadership_bonus_pct": leadership_bonus_pct,
            "project_depth_bonus_pct": depth_bonus_pct,
            "boosted_raw_pct": boosted_raw_pct,
            "final_score": final_score,
            "component": component
        }
