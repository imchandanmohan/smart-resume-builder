import os
import sys
import time
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)

import json
from pathlib import Path
import numpy as np
import streamlit as st
from rapidfuzz import fuzz

# Custom imports
from config.paths_config import *
from src.custom_exception import CustomException
from src.logger import get_logger
from src.ner.ner_service import NERService
from utils.text_cleaner import smart_post_process_regex, merge_broken_tokens_and_clean
from src.extractors.resume_llm_extractor import ResumeLLMExtractor
from src.extractors.jd_llm_extractor import JDLLMExtractor
from utils.common_functions import convert_pdf_to_text
from src.ner_highlighter import ResumeNERHighlighter

# Initialize logger
logger = get_logger(__name__)

# Initialize NER Service
ner_service = NERService()

def save_bytes_to_file(bytes_data, file_path):
    try:
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(bytes_data)
        logger.info(f"Saved bytes to {file_path}")
    except Exception as e:
        logger.error("Error saving bytes to file", exc_info=True)
        raise CustomException(e, sys)

def extract_resume(resume_bytes):
    try:
        save_bytes_to_file(resume_bytes, RESUME_FILE_PATH)
        convert_pdf_to_text(RESUME_FILE_PATH, PROCESSED_RESUME_TEXT_FILE_PATH)

        # ✨ Ensure text file is written and non-empty
        timeout_seconds = 3
        start_time = time.time()
        while (
            not os.path.exists(PROCESSED_RESUME_TEXT_FILE_PATH)
            or os.stat(PROCESSED_RESUME_TEXT_FILE_PATH).st_size == 0
        ):
            if time.time() - start_time > timeout_seconds:
                raise CustomException("Processed resume text file was not ready in time.")
            time.sleep(0.1)

        extractor = ResumeLLMExtractor(
            txt_path=PROCESSED_RESUME_TEXT_FILE_PATH,
            output_path=PROCESSED_RESUME_JSON_FILE_PATH
        )
        extractor.extract()

        logger.info("Resume extracted successfully")

    except Exception as e:
        logger.error("Error extracting resume", exc_info=True)
        raise CustomException(e, sys)

def extract_job_description(jd_text):
    try:
        save_bytes_to_file(jd_text.encode('utf-8'), JOB_DESCRIPTION_PATH)

        extractor = JDLLMExtractor(
            txt_path=JOB_DESCRIPTION_PATH,
            output_path=PROCESSED_JOB_DESCRIPTION_PATH
        )
        extractor.extract()

        # ✨ Wait for processed job-description text file to be written and non-empty
        timeout_seconds = 3
        start_time = time.time()
        while (
            not os.path.exists(PROCESSED_JOB_DESCRIPTION_PATH)
            or os.stat(PROCESSED_JOB_DESCRIPTION_PATH).st_size == 0
        ):
            if time.time() - start_time > timeout_seconds:
                raise CustomException("Processed job-description text file was not ready in time.")
            time.sleep(0.1)

        logger.info("Job description extracted successfully")

    except Exception as e:
        logger.error("Error extracting job description", exc_info=True)
        raise CustomException(e, sys)

def extract_text_after_about_the_job(text):
    try:
        split_text = text.split("About the job", 1)
        if len(split_text) < 2:
            logger.warning("'About the job' section not found in job description.")
            return ""
        return split_text[1].strip()
    except Exception as e:
        logger.error("Error extracting text after 'About the job'", exc_info=True)
        raise CustomException(e, sys)

def split_into_chunks(text, max_words=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def run_ner_and_save(text_path, output_path, is_jobdescription):
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        if is_jobdescription:
            clean_text = extract_text_after_about_the_job(raw_text)
        else:
            clean_text = raw_text

        if not clean_text.strip():
            logger.warning("No valid text found after 'About the job'. Skipping NER.")
            return

        text_chunks = split_into_chunks(clean_text, max_words=300)

        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as out_f:
            logger.info(f"Total chunks to process: {len(text_chunks)}")
            for idx, chunk in enumerate(text_chunks):
                if not chunk.strip():
                    logger.warning(f"Chunk {idx} is empty, skipping.")
                    continue

                # small pause to smooth out processing
                time.sleep(0.1)

                print(f"Processing chunk {idx + 1}:")
                print(chunk[:300])

                result = ner_service.predict(chunk)
                entities = result['entities']
                entities = smart_post_process_regex(entities)
                entities = merge_broken_tokens_and_clean(entities)

                # Convert np.float32 to float
                for ent in entities:
                    if isinstance(ent.get('score'), np.float32):
                        ent['score'] = float(ent['score'])

                final_result = {
                    "text": result['text'],
                    "entities": entities
                }

                json_line = json.dumps(final_result)
                out_f.write(json_line + "\n")

        logger.info(f"NER output saved to {output_path}")

    except Exception as e:
        logger.error("Error running NER and saving output", exc_info=True)
        raise CustomException(e, sys)

def extract_texts_from_resume_json(resume_json_path):
    try:
        with open(resume_json_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)

        extracted_texts = []

        # Education descriptions
        education = resume_data.get("education", [])
        for edu in education:
            description = edu.get("description")
            if description:
                extracted_texts.append({
                    "source": "education",
                    "text": description
                })

        # Work experience responsibilities
        work_experience = resume_data.get("work_experience", [])
        for work in work_experience:
            responsibilities = work.get("responsibilities", [])
            for responsibility in responsibilities:
                if responsibility:
                    extracted_texts.append({
                        "source": "work_experience",
                        "text": responsibility
                    })

        # Project descriptions
        projects = resume_data.get("projects", [])
        for project in projects:
            descriptions = project.get("description", [])
            for desc in descriptions:
                if desc:
                    extracted_texts.append({
                        "source": "projects",
                        "text": desc
                    })

        return extracted_texts

    except Exception as e:
        logger.error("Error extracting texts from resume JSON", exc_info=True)
        raise CustomException(e, sys)

def run_ner_on_extracted_texts(extracted_texts, output_path):
    try:
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as out_f:
            logger.info(f"Total extracted texts to process: {len(extracted_texts)}")

            for idx, item in enumerate(extracted_texts):
                text = item["text"]
                source = item["source"]

                if not text.strip():
                    logger.warning(f"Extracted text {idx} is empty, skipping.")
                    continue

                print(f"Processing {source} chunk {idx + 1}:")
                print(text[:300])

                result = ner_service.predict(text)
                entities = result['entities']
                entities = smart_post_process_regex(entities)
                entities = merge_broken_tokens_and_clean(entities)

                # Convert np.float32 to float
                for ent in entities:
                    if isinstance(ent.get('score'), np.float32):
                        ent['score'] = float(ent['score'])

                final_result = {
                    "source": source,
                    "original_text": text,
                    "ner_result": {
                        "text": result['text'],
                        "entities": entities
                    }
                }

                json_line = json.dumps(final_result)
                out_f.write(json_line + "\n")

        logger.info(f"NER output from extracted texts saved to {output_path}")

    except Exception as e:
        logger.error("Error running NER on extracted texts", exc_info=True)
        raise CustomException(e, sys)

def process_resume_and_jd(resume_bytes, job_description):
    try:
        # Step 1: Save resume_bytes to a temporary file
        extract_resume(resume_bytes)

        # Step 3: Save the job description text
        with open(JOB_DESCRIPTION_PATH, "wb") as f:
            f.write(job_description.encode('utf-8'))

        # Step 4: Process job description
        jd_text = job_description
        extract_job_description(jd_text)

        # Step 5: Run NER and highlight resume
        run_ner_and_save(PROCESSED_RESUME_TEXT_FILE_PATH, PROCESSED_RESUME_NER_PATH, False)
        process_resume_from_json()
        run_ner_and_save(JOB_DESCRIPTION_PATH, PROCESSED_JOB_DESCRIPTION_NER_PATH, True)
        
        rh = ResumeNERHighlighter(RESUME_FILE_PATH, PROCESSED_RESUME_NER_PATH)
        rh.process(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH)

        # Optional: Clean up the temp file
        #os.remove("temp_resume.pdf")"""


    except Exception as e:
        logger.error("Error processing resume and job description", exc_info=True)
        raise CustomException(e, sys)

# New for only processing JSON-based resume
def process_resume_from_json():
    try:
        extracted_texts = extract_texts_from_resume_json(PROCESSED_RESUME_JSON_FILE_PATH)
        run_ner_on_extracted_texts(extracted_texts, PROCESSED_RESUME_NER_PATH)

    except Exception as e:
        logger.error("Error processing resume from JSON", exc_info=True)
        raise CustomException(e, sys)

if __name__ == "__main__":
    try:
        logger.info("Pipeline started ✅")

        with open(RESUME_FILE_PATH, "rb") as f:
            resume_bytes = f.read()

        with open(JOB_DESCRIPTION_PATH, "r", encoding="utf-8") as f:
            jd_text = f.read()

        process_resume_and_jd(resume_bytes, jd_text)

        logger.info("Pipeline finished ✅")
        print("✅ Successfully processed resume and job description.")

    except Exception as e:
        logger.error(f"Pipeline failed ❌: {e}", exc_info=True)
        print(f"❌ Failed to process: {e}")
        sys.exit(1)
