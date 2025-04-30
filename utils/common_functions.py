import os
from fpdf import FPDF
import fitz
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import re
import string
from nltk.corpus import stopwords
import smtplib
import json
from email.message import EmailMessage
from config.paths_config import (
    PROCESSED_RESUME_JSON_FILE_PATH,
    PROCESSED_JOB_DESCRIPTION_PATH,
    PROCESSED_RESUME_HIGHLIGHTER_NER_PATH
)
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")


logger = get_logger(__name__)
STOPWORDS = set(stopwords.words('english'))


def convert_pdf_to_text(pdf_file, output_path=None):
    """
    Extracts text content from a PDF file and saves it as a .txt file.

    Parameters:
    pdf_file (str): Path to the PDF file.
    output_path (str, optional): Directory where the extracted text will be saved.
                                 If None, the predefined path (TEMPFILES_TEXTFILE) is used.

    Returns:
    str: Extracted text from the PDF.

    Raises:
    CustomException: If the file does not exist, the output path is invalid, or reading fails.
    """

    logger.info(f"PDF to text conversion started for file: {pdf_file}")

    if not os.path.exists(pdf_file):
        logger.error(f"The PDF file {pdf_file} does not exist.")
        raise CustomException("The PDF file does not exist.")

    if not output_path:
        # Use predefined TEMPFILES_TEXTFILE if no output_path is provided
        logger.info(f"No output path provided. Using predefined path: {output_path}")
    
    # Ensure the directory exists for saving the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        text = ""
        with fitz.open(pdf_file) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()
                logger.debug(f"Extracted text from page {page_num}")
                text += page_text

        # Write the extracted text to the predefined or provided output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        logger.info(f"Successfully saved extracted text to: {output_path}")
        return text

    except Exception as e:
        logger.exception("Failed to extract text from PDF.")
        raise CustomException("Error during PDF to text conversion.", e)
    

def send_job_summary_email():
    try:
        # Load resume JSON
        with open(PROCESSED_RESUME_JSON_FILE_PATH, "r") as f:
            resume = json.load(f)

        # Load JD JSON
        with open(PROCESSED_JOB_DESCRIPTION_PATH, "r") as f:
            jd_data = json.load(f)

        # Extract email and job details
        user_email = resume.get("email")
        full_name = resume.get("full_name", "Candidate")
        job = jd_data["job_details"]
        company = job.get("company_name", "Company")
        job_title = job.get("job_title", "Job")
        description = job.get("job_description", "")
        responsibilities = job.get("responsibilities", [])
        skills = job.get("skills_required", [])

        if not user_email:
            raise ValueError("No email found in resume data")

        # Compose HTML body
        html_body = f"""
        <h2>Your Resume for <i>{job_title}</i> at <i>{company}</i></h2>
        <p><b>Job Description:</b> {description}</p>
        <p><b>Responsibilities:</b></p>
        <ul>{"".join(f"<li>{r}</li>" for r in responsibilities)}</ul>
        <p><b>Required Skills:</b></p>
        <ul>{"".join(f"<li>{s}</li>" for s in skills)}</ul>
        <p>We’ve also attached your resume with the most relevant experience highlighted for ATS readability.</p>
        """

        # Setup email
        msg = EmailMessage()
        msg["Subject"] = f"Your Resume for {job_title} at {company}"
        msg["From"] = GMAIL_USER
        msg["To"] = user_email
        msg.set_content(
            f"Hi {full_name},\n\nAttached is your highlighted resume for the role '{job_title}' at {company}.\n\nPlease view this email in HTML format to see the job summary."
        )
        msg.add_alternative(html_body, subtype='html')

        # Attach highlighted resume PDF
        with open(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH, "rb") as f:
            pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename="highlighted_resume.pdf",
                disposition='attachment'
            )

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent to {user_email}")

    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        raise CustomException("Email delivery failed.", e)