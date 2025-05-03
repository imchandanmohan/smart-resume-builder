# modules/similarity.py

import pickle
from typing import List, Dict, Union
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import numpy as np


class SimilarityCalculator:
    """
    Loads a pre-trained TF-IDF model to compute similarity between resume and JD tokens.
    Falls back to SBERT embeddings if there's no TF-IDF overlap.
    """

    def __init__(
        self,
        tfidf_model_path: str = "models/tfidf_combined.pkl",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        # 🔹 Load pre-trained TF-IDF vectorizer
        with open(tfidf_model_path, "rb") as f:
            self.vectorizer = pickle.load(f)
        print("✅ Loaded TF-IDF model from:", tfidf_model_path)
        print(f"📚 TF-IDF Vocabulary size: {len(self.vectorizer.vocabulary_)}")

        # 🔹 Load SBERT model for fallback
        self.embedding_model = SentenceTransformer(embedding_model)

    def get_match_quality(self, score: float) -> str:
        if score >= 75:
            return "Excellent Fit"
        elif score >= 50:
            return "Good Fit"
        elif score >= 25:
            return "Partial Match"
        return "Needs Improvement"

    def compute_from_tokens(
        self, resume_tokens: List[str], jd_tokens: List[str]
    ) -> Dict[str, Union[float, str, Dict[str, Union[str, float, List[str]]]]]:
        r_text = " ".join(resume_tokens)
        j_text = " ".join(jd_tokens)

        vecs = self.vectorizer.transform([r_text, j_text])
        explanation = {}
        
        if vecs.nnz == 0:
            emb1 = self.embedding_model.encode(r_text, convert_to_tensor=True)
            emb2 = self.embedding_model.encode(j_text, convert_to_tensor=True)
            sim = float(util.pytorch_cos_sim(emb1, emb2)[0][0])
            score = float(round(sim * 100, 2))

            explanation["reason"] = "Fallback to SBERT – no TF-IDF keyword overlap"
            explanation["suggestion"] = "Consider adding more keywords from the job description to your resume"
            explanation["match_type"] = "semantic only"
            explanation["token_overlap"] = 0

            return {
                "score": score,
                "status": "embed_fallback",
                "message": self.get_match_quality(score),
                "explanation": explanation
            }

        sim = cosine_similarity(vecs[0], vecs[1])[0][0]
        score = float(round(sim * 100, 2))
        common_tokens = set(resume_tokens) & set(jd_tokens)
        overlap_percent = round(len(common_tokens) / len(set(jd_tokens)) * 100, 2)

        if score >= 75:
            tip = "Strong alignment – highlight key projects or achievements in the summary section."
        elif score >= 50:
            tip = "Good fit – consider adding more role-specific skills or keywords."
        elif score >= 25:
            tip = "Partial match – try matching more core responsibilities and tools."
        else:
            tip = "Weak alignment – tailor your resume more carefully to the job."

        explanation = {
            "match_type": "TF-IDF cosine",
            "token_overlap": f"{len(common_tokens)} / {len(set(jd_tokens))} = {overlap_percent}%",
            "reason": "Resume shares keywords with the job description",
            "suggestion": tip
        }

        return {
            "score": score,
            "status": "tfidf",
            "message": self.get_match_quality(score),
            "explanation": explanation
        }
