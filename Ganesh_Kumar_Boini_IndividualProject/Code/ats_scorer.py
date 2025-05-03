# modules/analysis/ats_scorer.py

from typing import Dict, Any

# NER service
from NER.ner_service import NERService

# 1) NER-based Keyword Matcher
from modules.analysis.keyword_analyzer_ner import KeywordAnalyzerNER

# 2) Combined JSON+Text+NER Competency Matcher
from modules.analysis.competency_matcher import CombinedCompetencyMatcher

# 3) Experience Alignment
from modules.analysis.experience_extractor import ExperienceExtractor

# 4) Sentence Impact
from modules.analysis.sentence_impact_checker import SentenceImpactAnalyzer

# 5) ATS Compliance
from modules.analysis.ats_compliance import ATSComplianceChecker

# 6) JD Mirroring
from modules.analysis.jd_mirror_checker import JDMirrorChecker

# Uniform ScoreComponent
from modules.analysis.score_component import ScoreComponent


class ATSScorer:
    """
    Orchestrates all components to compute a final ATS score out of 100:
      • Keyword Match (K)          – 25 pts (NER-based)
      • Competency Match (C)       – 25 pts
      • Experience Alignment (E)   – 20 pts
      • Sentence Impact (S)        – 20 pts
      • ATS Compliance (F)         – 5 pts
      • JD Mirroring (J)           – 5 pts
    """

    def __init__(self):
        ner = NERService()

        self.keyword     = KeywordAnalyzerNER(
            ner_service=ner.predict,
            use_sbert=True,
            semantic_threshold=0.75,
            use_fuzzy=True,
            fuzzy_threshold=85
        )
        self.competency  = CombinedCompetencyMatcher(weight=25.0)
        self.experience  = ExperienceExtractor()
        self.sentence    = SentenceImpactAnalyzer(skill_set=set())
        self.ats_compliance = ATSComplianceChecker
        self.jd_mirror   = JDMirrorChecker()

    def compute_ats_score(
        self,
        resume_json: Dict[str, Any],
        resume_text: str,
        jd_json: Dict[str, Any],
        jd_text: str,
        file_extension: str = ".txt"
    ) -> Dict[str, Any]:

        # 1) Keyword Match
        kw_res  = self.keyword.analyze_keywords(resume_text, jd_text)
        kw_comp: ScoreComponent = kw_res["component"]

        # 2) Competency Match
        comp_res  = self.competency.compute_component(resume_json, jd_json)
        comp_comp: ScoreComponent = comp_res["component"]

        # 3) Experience Alignment
        exp_res   = self.experience.calculate_experience_alignment(
            resume_json=resume_json,
            resume_text=resume_text,
            jd_json=jd_json,
            jd_text=jd_text
        )
        exp_comp: ScoreComponent = exp_res["component"]

        # 4) Sentence Impact
        sent_res  = self.sentence.analyze_sentences(resume_text, jd_text)
        sent_comp: ScoreComponent = sent_res["component"]

        # 5) ATS Compliance
        # 5) ATS Compliance
        ats_chk = self.ats_compliance(resume_text, jd_text, file_extension)
        compliance = ats_chk.evaluate()
        # grab the component your standalone test built
        comp_f: ScoreComponent = compliance["component"]


        # 6) JD Mirroring
        jm_res   = self.jd_mirror.analyze_section_order(resume_text, jd_text)
        jm_score = jm_res.get("section_order_score", 0.0)
        raw_j_pct= round(jm_score * 100, 2)
        comp_j = ScoreComponent(
            name="JD Mirroring",
            weight=5.0,
            raw=raw_j_pct,
            score=round(jm_score * 5, 2),
            notes=jm_res.get("notes", [])
        )

        # Final aggregation
        final_score = round(
            kw_comp.score +
            comp_comp.score +
            exp_comp.score +
            sent_comp.score +
            comp_f.score +
            comp_j.score
        , 2)

        return {
            "final_ats_score": final_score,
            "components": {
                "keyword_match":        kw_comp,
                "competency_match":     comp_comp,
                "experience_alignment": exp_comp,
                "sentence_impact":      sent_comp,
                "ats_compliance":       comp_f,
                "jd_mirroring":         comp_j
            },
            "diagnostics": {
                "keyword": {
                    "match_percent":       kw_res["match_percent"],
                    "common_hard_skills":  kw_res["common_hard_skills"],
                    "missing_hard_skills": kw_res["missing_hard_skills"]
                },
                "competency": {
                    "matched_required":   comp_res["matched_required"],
                    "missing_required":   comp_res["missing_required"],
                    "matched_preferred":  comp_res["matched_preferred"],
                    "missing_preferred":  comp_res["missing_preferred"]
                },
                "experience": {
                    "years_of_experience":     exp_res["years_of_experience"],
                    "leadership_bonus_pct":    exp_res["leadership_bonus_pct"],
                    "project_depth_bonus_pct": exp_res["project_depth_bonus_pct"]
                },
                "sentence": {
                    "action_ratio": sent_res["action_ratio"],
                    "metric_ratio": sent_res["metric_ratio"],
                    "impact_ratio": sent_res["impact_ratio"]
                },
                "compliance": compliance,
                "jd_mirroring": jm_res
            }
        }
