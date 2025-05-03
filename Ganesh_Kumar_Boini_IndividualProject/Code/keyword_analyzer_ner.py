# modules/analysis/keyword_analyzer_ner.py

from typing import List, Dict, Any, Set
from rapidfuzz import process as rapidfuzz_process
from sentence_transformers import SentenceTransformer, util
from modules.analysis.score_component import ScoreComponent

class KeywordAnalyzerNER:
    """
    Uses your NER service to extract HARD skills from resume and job description,
    then computes an overlap score, with optional SBERT semantic and RapidFuzz
    fuzzy matching layers.
    """
    def __init__(
        self,
        ner_service,                    # function: ner_service(text) -> List of entities
        use_sbert: bool       = False,
        semantic_threshold: float = 0.75,
        use_fuzzy: bool       = False,
        fuzzy_threshold: int  = 85
    ):
        self.ner_service = ner_service
        self.use_sbert = use_sbert
        self.semantic_threshold = semantic_threshold
        self.use_fuzzy = use_fuzzy
        self.fuzzy_threshold = fuzzy_threshold

        if self.use_sbert:
            self.sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

    def _extract_hard(self, labelled_entities: List[Any]) -> Set[str]:
        """
        Normalize any entity list (tuples, dicts, or multi-length sequences)
        into a set of lowercased tokens whose label == "HARD".
        """
        hard = set()
        for ent in labelled_entities:
            token, label = None, None

            # Tuple or list, e.g. (token,label) or (token,label,score)
            if isinstance(ent, (list, tuple)):
                if len(ent) >= 2:
                    token, label = ent[0], ent[1]

            # Dict style, e.g. {"text":..., "label":...}
            elif isinstance(ent, dict):
                token, label = ent.get("text"), ent.get("label")

            # Otherwise skip
            if not token or not label:
                continue

            if label.upper() == "HARD":
                hard.add(token.lower())
        return hard

    def analyze_keywords(
        self,
        resume_text: str,
        job_description_text: str
    ) -> Dict[str, Any]:
        # 1) Call NER and unwrap if it’s a dict
        resume_out = self.ner_service(resume_text)
        jd_out     = self.ner_service(job_description_text)

        raw_resume_ents = resume_out["entities"] if isinstance(resume_out, dict) else resume_out
        raw_jd_ents     = jd_out["entities"]     if isinstance(jd_out,     dict) else jd_out

        # 2) Robustly extract HARD tokens
        resume_hard = self._extract_hard(raw_resume_ents)
        jd_hard     = self._extract_hard(raw_jd_ents)

        # 3) Exact-match overlap
        exact_matches  = resume_hard & jd_hard
        missing_skills = jd_hard - exact_matches

        # 4) Optional SBERT semantic matching
        if self.use_sbert and missing_skills and resume_hard:
            res_list  = list(resume_hard)
            miss_list = list(missing_skills)
            res_emb   = self.sbert_model.encode(res_list,  convert_to_tensor=True)
            miss_emb  = self.sbert_model.encode(miss_list, convert_to_tensor=True)
            sim       = util.pytorch_cos_sim(res_emb, miss_emb)
            for j, jd_tok in enumerate(miss_list):
                if any(sim[:, j] > self.semantic_threshold):
                    exact_matches.add(jd_tok)
            missing_skills = jd_hard - exact_matches

        # 5) Optional RapidFuzz fuzzy matching
        if self.use_fuzzy and missing_skills and resume_hard:
            for jd_tok in list(missing_skills):
                match = rapidfuzz_process.extractOne(
                    jd_tok,
                    resume_hard,
                    score_cutoff=self.fuzzy_threshold
                )
                if match:
                    _, score_val, _ = match
                    if score_val >= self.fuzzy_threshold:
                        exact_matches.add(jd_tok)
            missing_skills = jd_hard - exact_matches

        # 6) Build component
        total_jd = len(jd_hard) or 1
        match_pct = round(len(exact_matches) / total_jd * 100, 2)
        component = ScoreComponent(
            name="Keyword Match",
            weight=25,
            raw=match_pct,
            score=round(match_pct * 0.25, 2),
            notes=[
                f"Matched HARD skills: {len(exact_matches)}/{total_jd}",
                f"SBERT semantic layer: {'on' if self.use_sbert else 'off'}",
                f"RapidFuzz fuzzy layer: {'on' if self.use_fuzzy else 'off'}"
            ]
        )

        return {
            "common_hard_skills":  exact_matches,
            "missing_hard_skills": missing_skills,
            "match_percent":       match_pct,
            "component":           component
        }
