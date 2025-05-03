# modules/analysis/jd_mirror_checker.py

import os
import re
import json
from typing import List, Dict, Union
from sentence_transformers import SentenceTransformer, util
from modules.analysis.score_component import ScoreComponent

class JDMirrorChecker:
    """
    Enhanced JD Mirroring:
      • 3 pts for covering JD labels (keywords/phrases)
      • 1 pt for bullet‐count similarity
      • 1 pt structure bonus (Projects > Education if hands-on JD)
    """

    def __init__(self,
                 jd_json_path: str = None,
                 sim_threshold: float = 0.75):
        # ── Locate JD JSON ──────────────
        if jd_json_path is None:
            # try common relative paths
            for p in ("data/job_description.json", "job_description.json"):
                if os.path.exists(p):
                    jd_json_path = p
                    break
        # ── Load JD data ────────────────
        try:
            jd_raw = json.load(open(jd_json_path))
        except Exception:
            jd_raw = {}
        jd = jd_raw.get("job_details", jd_raw)

        # ── Gather labels ───────────────
        top_kw   = jd.get("top_keywords_for_ATS", [])
        hpa      = jd_raw.get("hidden_patterns_analysis", {})
        industry = hpa.get("industry_keywords_detected", []) or []
        problems = hpa.get("problem_types_mentioned", [])   or []
        resps    = jd.get("responsibilities", [])           or []
        quals    = jd.get("qualifications", [])              or []

        # Clean responsibility & qualification phrases
        clean_phrases = [
            re.sub(r"[^a-z0-9\s]", "", p.lower()).strip()
            for p in (resps + quals)
        ]

        # Combine and dedupe
        combined = top_kw + industry + problems + clean_phrases
        seen = set()
        self.jd_labels: List[str] = []
        for lbl in combined:
            l = lbl.lower().strip()
            if l and l not in seen:
                seen.add(l)
                self.jd_labels.append(l)

        # ── SBERT for semantic matching ──
        self.sbert         = SentenceTransformer("all-MiniLM-L6-v2")
        self.sim_threshold = sim_threshold

        # ── Bullet distribution target ──
        self.jd_bullets = max(len(resps), 1)

        # ── Hands-on terms ──────────────
        self.hands_on_terms = {"hands-on", "practical experience", "projects"}

        # ── Section headers to detect ────
        self.section_keywords = [
            "summary", "objective", "skills", "technical skills", "projects",
            "technical projects", "experience", "work experience", "education",
            "certifications", "publications", "awards", "volunteer",
            "extracurricular", "activities"
        ]

    def extract_section_headers(self, text: str) -> List[str]:
        headers = []
        for line in text.splitlines():
            clean = re.sub(r"[^a-z\s]", "", line.strip().lower())
            if any(re.search(rf"\b{kw}\b", clean) for kw in self.section_keywords):
                headers.append(clean)
        return headers

    def count_resume_bullets(self, text: str) -> int:
        cnt = 0
        for line in text.splitlines():
            if re.match(r"^\s*[\-\*\•]\s", line) or re.match(r"^\s*\d+\.\s", line):
                cnt += 1
        return max(cnt, 1)

    def analyze_section_order(
        self,
        resume_text: str,
        jd_text: str
    ) -> Dict[str, Union[ScoreComponent, float, int, List[str]]]:
        rt_lower = resume_text.lower()

        # ── 1) Label coverage (up to 3 pts) ─────────────────
        labels = self.jd_labels
        total_labels = len(labels) or 1
        matched = []

        if labels:
            # embed JD labels and resume sentences
            jd_emb   = self.sbert.encode(labels,   convert_to_tensor=True)
            sents    = [s for s in re.split(r"[.\n]", rt_lower) if s.strip()]
            sent_emb = self.sbert.encode(sents,    convert_to_tensor=True)
            sim_mat  = util.pytorch_cos_sim(jd_emb, sent_emb)

            for i, lbl in enumerate(labels):
                if (sim_mat[i] >= self.sim_threshold).any():
                    matched.append(lbl)

        label_score = len(matched) / total_labels * 3.0

        # ── 2) Bullet-count similarity (up to 1 pt) ───────────
        resume_bullets = self.count_resume_bullets(resume_text)
        diff = abs(resume_bullets - self.jd_bullets)
        bullet_score = max(0.0, 1.0 - diff / self.jd_bullets)

        # ── 3) Structure bonus (up to 1 pt) ─────────────────
        bonus = 0.0
        if any(term in jd_text.lower() for term in self.hands_on_terms):
            secs = self.extract_section_headers(resume_text)
            try:
                p = next(i for i,s in enumerate(secs) if "projects" in s)
                e = next(i for i,s in enumerate(secs) if "education" in s)
                if p < e:
                    bonus = 1.0
                # else no bonus
            except StopIteration:
                pass

        # ── 4) Combine & cap at 5 pts ────────────────────────
        total_pts = min(label_score + bullet_score + bonus, 5.0)
        raw_pct   = round(total_pts / 5.0 * 100, 2)

        # ── 5) Build notes & component ───────────────────────
        notes = [
            f"JD labels matched: {len(matched)}/{total_labels} → {round(label_score,2)}/3pt",
            f"Bullet count: resume {resume_bullets} vs JD {self.jd_bullets} → {round(bullet_score,2)}/1pt"
        ]
        if bonus:
            notes.append("✅ Projects prioritized above Education → +1pt")

        component = ScoreComponent(
            name="JD Mirroring",
            weight=5,
            raw=raw_pct,
            score=round(total_pts, 2),
            notes=notes
        )

        return {
            "component": component,
            "matched_labels": matched,
            "total_labels": total_labels,
            "bullet_score": round(bullet_score,2),
            "bonus_pts": bonus,
            "section_order_score": round(total_pts,2),
            "notes": notes
        }
