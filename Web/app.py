import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import base64
import time
from pathlib import Path
from src.extractors.resume_llm_extractor import ResumeLLMExtractor
from src.extractors.jd_llm_extractor import JDLLMExtractor
from config.paths_config import *
from utils.common_functions import convert_pdf_to_text
from utils.text_cleaner import smart_post_process_regex, merge_broken_tokens_and_clean
from src.ner.ner_service import NERService
from src.analyse_pipeline import process_resume_and_jd
from src.ats_score import ATSResumeAnalyzer
from src.analyze_jd_focus import analyze_job_description_focus
from src.ner.extract_resume_ner import extract_resume_ner
from utils.common_functions import send_job_summary_email
# Set correct absolute path from project root
ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'processed', 'jb_ner.jsonl'))

# --------------------------------------------------
# PAGE‑LEVEL CONFIG & SESSION STATE
# --------------------------------------------------
st.set_page_config(page_title="Smart Resume Builder", layout="wide")

if "page" not in st.session_state:           # <upload | analysis | final>
    st.session_state.page = "upload"

a_keys = ("resume_bytes", "resume_name", "job_description")
for k in a_keys:
    st.session_state.setdefault(k, None)

# --------------------------------------------------
# SHARED  STYLES / HEADER
# --------------------------------------------------
st.markdown(
    """
    <style>
        .header {background:#eee; color:#000; padding:1rem; border-radius:8px; margin-bottom:1.2rem; border:1px solid #d3d3d3;}
        .stTextArea textarea {border:1px solid #aaa !important;}
        .issue-label {font-weight:600; font-size:0.9rem; margin-top:0.3rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

def header():
    st.markdown(
        """
        <div class="header">
            <h2 style="margin:0;">Smart Resume Builder</h2>
            <p style="margin:0;">Single location for resume creation and job description analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# PAGE 1 – UPLOAD  (LEFT resume | RIGHT JD)
# --------------------------------------------------

def page_upload():
    header()

    col1, col2 = st.columns(2, gap="large")

    # ---- Resume Upload --------------------------------------------------
    with col1:
        st.subheader("📄 Your Resume")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            st.session_state.resume_bytes = uploaded_file.read()
            st.session_state.resume_name = "resume.pdf"

            with st.expander("Preview Resume", expanded=False):
                b64 = base64.b64encode(st.session_state.resume_bytes).decode()
                st.markdown(
                    f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='600'></iframe>",
                    unsafe_allow_html=True,
                )

    # ---- Job Description ------------------------------------------------
    with col2:
        st.subheader("📝 Job Description")
        jd_text = st.text_area(
            "Paste the job description here:",
            height=500,
            placeholder="Paste the full JD …",
        )
        if jd_text:
            st.session_state.job_description = jd_text

    # ---- Footer / NEXT --------------------------------------------------
    st.markdown("---")
    left, right = st.columns([3, 1])
    with left:
        if st.session_state.resume_bytes:
            st.info("✅ Resume uploaded")
        if st.session_state.job_description:
            st.info("✅ Job description added")

    with right:
        can_go_next = st.session_state.resume_bytes and st.session_state.job_description
        if st.button("Analyze ➡️", disabled=not can_go_next):
            st.session_state.page = "analysis"

            # Run the whole pipeline
            process_resume_and_jd(st.session_state.resume_bytes, st.session_state.job_description)

            # ✅ Only AFTER processing success, move to analysis page
            st.session_state.page = "analysis"

            st.rerun()

# --------------------------------------------------
# PAGE 2 – ANALYSIS  (SIDEBAR gauge  + 3‑TAB main)
# --------------------------------------------------

def sidebar_ats(ats_data):
    with st.sidebar:
        st.header("Match Rate")
        match_rate = ats_data.get("ATS_score", 0)
        st.markdown(
            f"""
            <div style='position:relative;width:140px;height:140px;margin:auto;'>
                <svg width='140' height='140'>
                    <circle cx='70' cy='70' r='60' stroke='#eee' stroke-width='14' fill='none'/>
                    <circle cx='70' cy='70' r='60' stroke='#4caf50' stroke-width='14' fill='none' 
                            stroke-dasharray='{match_rate*3.77} 999' stroke-dashoffset='75' stroke-linecap='round'/>
                </svg>
                <div style='position:absolute;top:45px;left:0;width:140px;text-align:center;font-size:28px;font-weight:700;'>{match_rate}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Upload & rescan")
        st.button("⚡ Power Edit")

        issues = ats_data.get("issues", {})
        for k, v in issues.items():
            st.markdown(f"<div class='issue-label'>{k} – {v} issue{'s' if v != 1 else ''} to fix</div>", unsafe_allow_html=True)
            st.progress(min(v / 12, 1.0))



def analytics_tab(ats_data):
    def row(msg, icon="ℹ️", color="info"):
        if color == "success":
            st.success(msg, icon=icon)
        elif color == "error":
            st.error(msg, icon=icon)
        elif color == "warning":
            st.warning(msg, icon=icon)
        else:
            st.info(msg, icon=icon)

    suggestions = ats_data.get("suggestions", [])

    if not suggestions:
        row("No suggestions found — your resume looks great!", "✅", "success")
    else:
        for item in suggestions:
            text = item.get("text", "")
            cat = item.get("category", "info")
            icon = {
                "error": "❌",
                "warning": "⚠️",
                "suggestion": "💡",
                "information": "ℹ️"
            }.get(cat, "ℹ️")
            row(text, icon=icon, color=cat)



def page_analysis():
    header()

    analyzer = ATSResumeAnalyzer()
    ats_data = analyzer.analyze()
    sidebar_ats(ats_data)

    tab1, tab2, tab3 = st.tabs(["ATS Analytics", "Job Description", "Resume"])

    with tab1:
        analytics_tab(ats_data)
        st.write("Page is commented")
    with tab2:
        st.header("📌 Job Description Focus Analysis")
        try:
            label_counts, summary = analyze_job_description_focus()

            st.subheader("Label Frequency")
            for label, count in label_counts:
                st.markdown(f"- **{label}**: {count} mentions")
                st.progress(min(count / 20, 1.0))  # bar length scaling

            st.markdown("---")
            st.subheader("💡 Insight")
            st.info(summary)

            st.markdown("---")
            st.subheader("📄 Original Job Description")
            st.write(st.session_state.job_description)

        except FileNotFoundError as e:
            st.error(str(e))
        

    with tab3:
        try:
            extract_resume_ner()
            st.subheader(st.session_state.resume_name or "Resume Preview")
            if not os.path.exists(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH):
                st.error(f"File not found at {PROCESSED_RESUME_HIGHLIGHTER_NER_PATH}")
            else:
                with open(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH, "rb") as f:
                    pdf_bytes = f.read()

                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(
                    f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='700'></iframe>",
                    unsafe_allow_html=True,
                )
        except FileNotFoundError:
            st.error("Highlighted resume not found. Please run the resume processing first.")

    st.markdown("---")
    if st.button("Next ➡️", key="final-btn"):
        st.session_state.page = "final"
        st.rerun()


# --------------------------------------------------
# PAGE 3 – FINAL VIEW
# --------------------------------------------------

def page_final():
    header()
    st.success("All set! Here's your resume after analysis (no edits applied in this demo).")

    if st.session_state.resume_bytes:
        if not os.path.exists(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH):
            st.error(f"File not found at {PROCESSED_RESUME_HIGHLIGHTER_NER_PATH}")
        else:
            with open(PROCESSED_RESUME_HIGHLIGHTER_NER_PATH, "rb") as f:
                pdf_bytes = f.read()

            b64 = base64.b64encode(pdf_bytes).decode()
            st.markdown(
                f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='700'></iframe>",
                unsafe_allow_html=True,
            )

    if st.button("Send Email"):
        send_job_summary_email()
        st.session_state.page = "upload"
        st.rerun()

# --------------------------------------------------
# ROUTER
# --------------------------------------------------
if st.session_state.page == "upload":
    page_upload()
elif st.session_state.page == "analysis":
    page_analysis()
else:
    page_final()

