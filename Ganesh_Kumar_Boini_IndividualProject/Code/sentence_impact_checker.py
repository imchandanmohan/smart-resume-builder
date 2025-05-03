# modules/analysis/sentence_impact_checker.py
import spacy
from typing import List, Dict, Union
from modules.analysis.score_component import ScoreComponent
from NER.ner_service import NERService  # your real service

_NLP = spacy.load("en_core_web_sm")

IMPACT_PRIORITY_TERMS = {
    "impact", "results-driven", "metrics",
    "quantify", "measurable", "outcomes", "performance"
}


class SentenceImpactAnalyzer:
    """
    Scores a resume’s bullets by how action- and
    impact-oriented they are, using NER labels.
    """

    def __init__(self, skill_set: set = None):
        self.skill_set = skill_set or set()
        self.ner = NERService()  # instantiate your NER client

    def _should_boost(self, jd_text: str) -> bool:
        jd_lower = jd_text.lower()
        return any(term in jd_lower for term in IMPACT_PRIORITY_TERMS)

    def analyze_sentences(
        self, resume_text: str, jd_text: str
    ) -> Dict[str, Union[int, float, ScoreComponent]]:
        # Segment sentences
        doc = _NLP(resume_text)
        sentences = [sent.text for sent in doc.sents]
        total = max(len(sentences), 1)

        # Counters
        action_cnt = metric_cnt = impact_cnt = skill_cnt = 0

        for sent in sentences:
            # Use predict() to get entities
            ner_out = self.ner.predict(sent)
            entities = ner_out.get("entities", [])

            # Build token–label pairs
            labels: List[tuple[str,str]] = [
                (ent["text"], ent["label"]) for ent in entities
            ]

            # Tally
            if any(lbl == "ACTION" for _, lbl in labels):
                action_cnt += 1
            if any(lbl == "METRIC" for _, lbl in labels):
                metric_cnt += 1
            if any(lbl == "IMPACT" for _, lbl in labels):
                impact_cnt += 1
            if any(lbl == "HARD"   for _, lbl in labels):
                skill_cnt += 1

        # Compute ratios
        action_ratio = round(action_cnt / total, 2)
        metric_ratio = round(metric_cnt / total, 2)
        impact_ratio = round(impact_cnt / total, 2)
        skill_ratio  = round(skill_cnt  / total, 2)

        # Weight logic
        base_w = 20.0
        weight = 25.0 if self._should_boost(jd_text) else base_w

        # Raw 0–1 metric
        raw = 0.4 * action_ratio + 0.3 * metric_ratio + 0.3 * impact_ratio
        raw_pct = round(raw * 100, 2)

        # Final score
        score = round(raw_pct * (weight / 100), 2)

        # Notes
        notes = []
        if action_cnt == 0: notes.append("No ACTION verbs")
        if metric_cnt == 0: notes.append("No METRIC tags")
        if impact_cnt == 0: notes.append("No IMPACT labels")
        if skill_cnt  == 0: notes.append("No HARD skills mentioned")
        if weight > base_w:
            notes.append(f"Boosted to {int(weight)} (JD emphasizes metrics)")

        component = ScoreComponent(
            name="Sentence Impact",
            weight=weight,
            raw=raw_pct,
            score=score,
            notes=notes or ["OK"],
        )

        return {
            "total_sentences": total,
            "action_verb_sentences": action_cnt,
            "metric_sentences": metric_cnt,
            "impact_sentences": impact_cnt,
            "skill_sentences": skill_cnt,
            "action_ratio": action_ratio,
            "metric_ratio": metric_ratio,
            "impact_ratio": impact_ratio,
            "skill_ratio": skill_ratio,
            "impact_score": score,
            "boosted_weight": weight,
            "component": component
        }
