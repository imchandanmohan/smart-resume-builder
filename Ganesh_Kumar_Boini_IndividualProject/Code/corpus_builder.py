# modules/extraction/corpus_builder.py

import os
import pandas as pd

class CorpusBuilder:
    """
    Handles building job, resume, and combined corpus CSVs.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Safely read a CSV file.

        Args:
            file_path (str): Path to CSV file.

        Returns:
            pd.DataFrame: Loaded DataFrame.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ File not found: {file_path}")
        return pd.read_csv(file_path)

    def create_job_corpus(self, job_file: str = "data/input/fake_job_postings.csv") -> pd.DataFrame:
        """
        Create job_corpus.csv from job postings file.

        Args:
            job_file (str): Path to the job postings CSV.

        Returns:
            pd.DataFrame: Job corpus DataFrame.
        """
        job_df = self._read_csv(job_file)
        job_corpus = job_df["description"].dropna().astype(str)
        job_corpus_df = pd.DataFrame({"id": range(1, len(job_corpus) + 1), "text": job_corpus})
        job_corpus_df.to_csv(os.path.join(self.data_dir, "processed/job_corpus.csv"), index=False)
        print("✅ Created: data/processed/job_corpus.csv")
        return job_corpus_df

    def create_resume_corpus(self, resume_file: str = "data/input/Resume.csv") -> pd.DataFrame:
        """
        Create resume_corpus.csv from resumes file.

        Args:
            resume_file (str): Path to the resumes CSV.

        Returns:
            pd.DataFrame: Resume corpus DataFrame.
        """
        resume_df = self._read_csv(resume_file)
        resume_corpus = resume_df["Resume_str"].dropna().astype(str)
        resume_corpus_df = pd.DataFrame({"id": range(1, len(resume_corpus) + 1), "text": resume_corpus})
        resume_corpus_df.to_csv(os.path.join(self.data_dir, "processed/resume_corpus.csv"), index=False)
        print("✅ Created: data/processed/resume_corpus.csv")
        return resume_corpus_df

    def combine_corpora(
        self,
        job_corpus_df: pd.DataFrame,
        resume_corpus_df: pd.DataFrame,
        output_file: str = "data/processed/full_corpus.csv"
    ) -> pd.DataFrame:
        """
        Combine job and resume corpora into one file.

        Args:
            job_corpus_df (pd.DataFrame): DataFrame of job corpus.
            resume_corpus_df (pd.DataFrame): DataFrame of resume corpus.
            output_file (str): Path to save the combined corpus.

        Returns:
            pd.DataFrame: Full combined corpus DataFrame.
        """
        full_corpus = pd.concat([job_corpus_df, resume_corpus_df], ignore_index=True)
        full_corpus.to_csv(output_file, index=False)
        print("✅ Created:", output_file)
        return full_corpus
