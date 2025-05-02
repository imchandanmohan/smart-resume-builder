from pathlib import Path

# Go up to project root
BASE_DIR = Path(__file__).resolve().parents[1]


############################### USER - Assets #############################

RESUME_DIR = BASE_DIR / "artifacts" / "resume" 
RESUME_FILE_PATH = RESUME_DIR / "resume.pdf"
PROCESSED_RESUME_TEXT_FILE_PATH = BASE_DIR / "artifacts" / "processed"/ "resume.txt"

JOB_DESCRIPTION_DIR =  BASE_DIR / "artifacts"/ "job description"
JOB_DESCRIPTION_PATH = JOB_DESCRIPTION_DIR / "job_description.txt"

PROCESSED_RESUME_JSON_FILE_PATH = BASE_DIR / "artifacts" / "processed"/ "resume.json"
PROCESSED_RESUME_NER_PATH = BASE_DIR / "artifacts" / "processed"/ "resume_ner.jsonl"
PROCESSED_JOB_DESCRIPTION_PATH = BASE_DIR / "artifacts" / "processed"/ "job_description.json"
PROCESSED_JOB_DESCRIPTION_NER_PATH = BASE_DIR / "artifacts" / "processed"/ "jb_ner.jsonl"

PROCESSED_RESUME_HIGHLIGHTER_NER_PATH = BASE_DIR / "artifacts" / "processed"/"highlighted_resume.pdf"

############################### Test File Location #############################

TEMPFILES_RESUME_DIR = BASE_DIR / "junk_files"
TEMPFILES_RESUME_FILE_PATH  = TEMPFILES_RESUME_DIR / "resume.pdf"
TEMPFILES_PROCESSED_RESUME_TEXT_FILE_PATH = TEMPFILES_RESUME_DIR / "resume.txt"


TEMPFILES_JOB_DESCRIPTION_DIR =  TEMPFILES_RESUME_DIR / "job_description"
TEMPFILES_JOB_DESCRIPTION_PATH = TEMPFILES_RESUME_DIR / "job_description.txt"

TEMPFILES_PROCESSED_RESUME_JSON_FILE_PATH = TEMPFILES_RESUME_DIR / "resume.json"
TEMPFILES_PROCESSED_JOB_DESCRIPTION_PATH = TEMPFILES_RESUME_DIR / "job_description.json"

