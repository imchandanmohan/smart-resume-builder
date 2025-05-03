"""
build_skill_taxonomy.py
Module to build a unified skill taxonomy from multiple skill sources.
"""

import os
import json
import pandas as pd
from typing import List, Set

class SkillTaxonomyBuilder:
    """
    Builds and saves a combined skill taxonomy from provided Excel sources.
    """

    def __init__(self, skills_path: str, tech_skills_path: str, output_path: str):
        self.skills_path = skills_path
        self.tech_skills_path = tech_skills_path
        self.output_path = output_path

    def load_skills(self) -> Set[str]:
        """Load skills from Excel files and return a set of unique skill names."""
        try:
            skills_df = pd.read_excel(self.skills_path)
            tech_df = pd.read_excel(self.tech_skills_path)

            base_skills = set(skills_df["Element Name"].dropna().unique())
            tech_skills = set(tech_df["Example"].dropna().unique())

            combined_skills = base_skills.union(tech_skills)
            print(f"✅ Loaded {len(combined_skills)} unique skills from sources.")
            return combined_skills

        except Exception as e:
            print(f"❌ Error loading skill files: {e}")
            return set()

    def save_taxonomy(self, skills: Set[str]) -> None:
        """Save the sorted skills into a JSON file."""
        try:
            sorted_skills = sorted(skills)
            with open(self.output_path, "w") as f:
                json.dump(sorted_skills, f, indent=2)
            print(f"✅ Skill taxonomy saved to {self.output_path}")

        except Exception as e:
            print(f"❌ Error saving skill taxonomy: {e}")

    def build(self) -> None:
        """Complete pipeline to load skills and save the taxonomy."""
        skills = self.load_skills()
        if skills:
            self.save_taxonomy(skills)


