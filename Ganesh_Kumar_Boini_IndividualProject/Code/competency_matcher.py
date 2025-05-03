# modules/analysis/combined_competency_matcher.py

import re
from typing import Dict, Any, List, Set
from NER.ner_service import NERService
from modules.analysis.score_component import ScoreComponent

class CombinedCompetencyMatcher:
    """
    Combines structured JSON, free-text parsing, and NER to compute
    a competency score for 'Required' and 'Preferred' skills.

    - Required skills (from JSON skills_required) count 1pt each.
    - Preferred qualifications (NER extracted from JSON qualifications) count 2pt each.
    - Resume skills come from JSON skills list, project technologies,
      free-text bullets, and NER on full resume text.
    """

    def __init__(self, weight: float = 25.0):
        self.weight = weight
        self.ner = NERService()

    def _extract_hard_from_text(self, text: str) -> Set[str]:
        """
        Use NERService.predict() to pull out HARD-labeled tokens from arbitrary text.
        """
        ents = self.ner.predict(text).get("entities", [])
        return {ent["text"].lower() for ent in ents if ent["label"] == "HARD"}

    def _extract_preferred_from_qualifications(self, qualifications: List[str]) -> Set[str]:
        """
        Run NER over each qualification sentence to harvest HARD skills.
        """
        pref = set()
        for qual in qualifications:
            ents = self.ner.predict(qual).get("entities", [])
            for ent in ents:
                if ent["label"] == "HARD":
                    pref.add(ent["text"].lower())
        return pref

    def compute_component(
        self, resume: Dict[str, Any], jd: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1️⃣ Required and Preferred lists from JSON
        required = [s.lower() for s in jd.get("skills_required", [])]
        preferred = sorted(self._extract_preferred_from_qualifications(
            jd.get("qualifications", [])
        ))

        # 2️⃣ Build resume skill set from JSON and free text
        resume_skills: Set[str] = {s.lower() for s in resume.get("skills", [])}

        # Add project technologies
        for proj in resume.get("projects", []):
            for tech in proj.get("technologies_used", []):
                resume_skills.add(tech.lower())

        # Flatten bullets from work_experience and project descriptions
        bullets: List[str] = []
        for exp in resume.get("work_experience", []):
            bullets += [b.lower() for b in exp.get("responsibilities", [])]
        for proj in resume.get("projects", []):
            desc = proj.get("description", "")
            if desc:
                bullets.append(desc.lower())

        # Substring match: add any required/preferred skill found in bullets
        for skill in required + preferred:
            if any(skill in b for b in bullets):
                resume_skills.add(skill)

        # NER extract HARD skills from full resume text
        full_text = "\n".join(bullets)
        resume_skills |= self._extract_hard_from_text(full_text)

        # 3️⃣ Compute matches
        matched_req  = [s for s in required  if s in resume_skills]
        matched_pref = [s for s in preferred if s in resume_skills]

        # 4️⃣ Scoring
        total_pts  = len(required) * 1 + len(preferred) * 2 or 1
        earned_pts = len(matched_req) * 1 + len(matched_pref) * 2

        raw_pct = round(earned_pts / total_pts * 100, 2)
        score   = round(raw_pct * (self.weight / 100), 2)

        # 5️⃣ ScoreComponent
        notes = [
            f"Required matched: {len(matched_req)}/{len(required)}",
            f"Preferred matched: {len(matched_pref)}/{len(preferred)}"
        ]
        component = ScoreComponent(
            name="Competency Match",
            weight=self.weight,
            raw=raw_pct,
            score=score,
            notes=notes
        )

        return {
            "component": component,
            "matched_required":  matched_req,
            "missing_required":  [s for s in required  if s not in matched_req],
            "matched_preferred": matched_pref,
            "missing_preferred": [s for s in preferred if s not in matched_pref],
        }
