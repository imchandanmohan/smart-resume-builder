import streamlit as st
import base64
import time
import smtplib
import ssl
import json
from email.message import EmailMessage
from pathlib import Path

# --------------------------------------------------
# PAGE-LEVEL CONFIG & SESSION STATE
# --------------------------------------------------
st.set_page_config(page_title="Smart Resume Builder", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "upload"

a_keys = ("resume_bytes", "resume_name", "job_description")
for k in a_keys:
    st.session_state.setdefault(k, None)

# LOAD RESUME EXTRACTION JSON
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / 'src' / 'TextExtraction' / 'resume_extraction.json'
try:
    with open(JSON_PATH, 'r') as f:
        resume_extraction_data = json.load(f)
except FileNotFoundError:
    st.error("resume_extraction.json file not found!")
    resume_extraction_data = {}
except Exception as e:
    st.error(f"Error loading resume_extraction.json: {str(e)}")
    resume_extraction_data = {}
# Extract email if present
contact_email = resume_extraction_data.get('contact', {}).get('email', None)

# --------------------------------------------------
# SHARED STYLES / HEADER
# --------------------------------------------------
st.markdown(
    """
    <style>
        .header {background:#000; color:#fff; padding:1rem; border-radius:8px; margin-bottom:1.2rem; border:1px solid #d3d3d3;}
        .stTextArea textarea {border:1px solid #fff !important;}
        .issue-label {font-weight:600; font-size:0.9rem; margin-top:0.3rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

def header():
    st.markdown(
        """
        <div class="header">
            <h2 style="margin:0; color:#ffffff;">Smart Resume Builder</h2>
            <p style="margin:0;">Single location for resume creation and job description analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# EMAIL SENDING FUNCTION
# --------------------------------------------------
def send_email(receiver_email, resume_bytes, resume_filename):
    sender_email = "dineshchandragaddam2002@gmail.com"
    sender_password = "rguw iwht zfun mjzd"  # Replace with your App Password
    msg = EmailMessage()
    msg['Subject'] = 'Your Resume from Smart Resume Builder'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Hello,\n\nHere is your resume as requested.\n\nBest regards,\nSmart Resume Builder Team")
    msg.add_attachment(resume_bytes, maintype='application', subtype='pdf', filename=resume_filename)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)

# --------------------------------------------------
# PAGE 1 – UPLOAD
# --------------------------------------------------
def page_upload():
    header()

    col1, col2 = st.columns(2, gap="large")

    # Resume uploader (with a key so it retains its value)
    with col1:
        st.subheader("📄 Your Resume")
        uploaded = st.file_uploader("Upload PDF", type=["pdf"], key="upload_uploader")
        if uploaded:
            st.session_state.resume_bytes = uploaded.read()
            st.session_state.resume_name = uploaded.name

        # Show preview if already uploaded
        if st.session_state.resume_bytes:
            with st.expander("Preview Resume", expanded=False):
                b64 = base64.b64encode(st.session_state.resume_bytes).decode()
                st.markdown(
                    f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='400'></iframe>",
                    unsafe_allow_html=True
                )

    # Job description textarea (value bound to session_state)
    with col2:
        st.subheader("📝 Job Description")
        jd = st.text_area(
            "Paste JD here:",
            value=st.session_state.job_description or "",
            height=600,
            key="jd_area"
        )
        if jd != st.session_state.job_description:
            st.session_state.job_description = jd

    st.markdown("---")

    # Status messages
    if st.session_state.resume_bytes:
        st.info("✅ Resume uploaded")
    if st.session_state.job_description:
        st.info("✅ Job description added")

    # Navigation buttons
    left,middle, right = st.columns([1,6, 1])
    
    with right:
        if st.session_state.resume_bytes and st.session_state.job_description:
            if st.button("Next ➡️"):
                st.session_state.page = "analysis"
                st.experimental_rerun()

# --------------------------------------------------
# PAGE 2 – ANALYSIS
# --------------------------------------------------
def sidebar_ats():
    with st.sidebar:
        st.header("Match Rate")
        MATCH_RATE = 76
        st.markdown(
            f"""
            <div style='position:relative;width:140px;height:140px;margin:auto;'>
                <svg width='140' height='140'>
                    <circle cx='70' cy='70' r='60' stroke='#eee' stroke-width='14' fill='none'/>
                    <circle cx='70' cy='70' r='60' stroke='#4caf50' stroke-width='14' fill='none' 
                            stroke-dasharray='{MATCH_RATE*3.77} 999' stroke-dashoffset='75' stroke-linecap='round'/>
                </svg>
                <div style='position:absolute;top:45px;left:0;width:140px;text-align:center;font-size:28px;font-weight:700;'>{MATCH_RATE}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        issues = {
            "Searchability": 8, "Hard Skills": 12, "Soft Skills": 4,
            "Recruiter Tips": 2, "Formatting": 1,
        }
        for k, v in issues.items():
            st.markdown(f"<div class='issue-label'>{k} – {v} issue{'s' if v!=1 else ''} to fix</div>", unsafe_allow_html=True)
            st.progress(min(v/12, 1.0))

def analytics_tab():
    def row(msg, icon="ℹ️", color="info"):
        if color == "success": st.success(msg, icon=icon)
        elif color == "error": st.error(msg, icon=icon)
        elif color == "warning": st.warning(msg, icon=icon)
        else: st.info(msg, icon=icon)
    row("Adding this job's company name and web address can help us provide you ATS-specific tips.", "❌", "error")
    row("You provided your physical address. Recruiters use your address to validate your location for job matches.", "✅", "success")
    row("You provided your email. Recruiters use your email to contact you for job matches.", "✅", "success")
    row("We did not find a phone number in your resume. Some recruiters prefer a phone call to email.", "❌", "error")
    row("We did not find a summary section on your resume …", "⚠️", "warning")
    row("We found the education section in your resume.", "✅", "success")
    row("We found the work experience section in your resume.", "✅", "success")
    row("The Machine Learning Engineer job title provided in the JD was not found in your resume …", "❌", "error")
    row("The dates in your work experience section are properly formatted.", "✅", "success")
    row("Your education does not match the required (bachelors)…", "❌", "error")
    row("You are using a .txt resume. Consider using an ATS compatible .pdf file instead.", "⚠️", "warning")
    row("Your file name doesn't contain special characters that could cause an error in ATS.", "✅", "success")
    row("Your file name is concise and readable.", "✅", "success")

def page_analysis():
    header()
    sidebar_ats()
    tab1, tab2, tab3 = st.tabs(["ATS Analytics", "Job Description", "Resume"])
    with tab1: analytics_tab()
    with tab2: st.subheader("Job Description"); st.write(st.session_state.job_description)
    with tab3:
        st.subheader(st.session_state.resume_name or "Resume Preview")
        if st.session_state.resume_bytes:
            b64 = base64.b64encode(st.session_state.resume_bytes).decode()
            st.markdown(
                f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='700'></iframe>", unsafe_allow_html=True,
            )
    st.markdown("---")
    left,middle, right = st.columns([1,6, 1])
    with left:
        if st.button("⬅️ Back"):
            st.session_state.page = "upload"
            st.experimental_rerun()
    with right:
        if st.button("Next ➡️"):
            st.session_state.page = "final"
            st.experimental_rerun()

# --------------------------------------------------
# PAGE 3 – FINAL VIEW
# --------------------------------------------------
def page_final():
    header()
    st.success("All set! Here's your resume after analysis.")
    if st.session_state.resume_bytes:
        b64 = base64.b64encode(st.session_state.resume_bytes).decode()
        st.markdown(
            f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='700'></iframe>", unsafe_allow_html=True,
        )
        st.markdown("---")
        st.subheader("📩 Email your resume")
        if contact_email:
            st.info(f"Using extracted email: {contact_email}")
            if st.button("Send Resume 📧"):
                with st.spinner("Sending email..."):
                    result = send_email(contact_email, st.session_state.resume_bytes, st.session_state.resume_name)
                    if result == True: st.success(f"✅ Resume sent successfully to {contact_email}!")
                    else: st.error(f"❌ Failed to send email: {result}")
        else:
            user_email = st.text_input("Enter your email address:")
            if st.button("Send Resume 📧"):
                if user_email:
                    with st.spinner("Sending email..."):
                        result = send_email(user_email, st.session_state.resume_bytes, st.session_state.resume_name)
                        if result == True: st.success(f"✅ Resume sent successfully to {user_email}!")
                        else: st.error(f"❌ Failed to send email: {result}")
                else: st.warning("⚠️ Please enter a valid email address.")
        st.download_button(
            label="⬇️ Download Resume",
            data=st.session_state.resume_bytes,
            file_name=st.session_state.resume_name,
            mime="application/pdf",
        )
    st.markdown("---")
    left, right = st.columns([1,1])
    with left:
        if st.button("⬅️ Back"):
            st.session_state.page = "analysis"
            st.experimental_rerun()

# --------------------------------------------------
# ROUTER
# --------------------------------------------------
if st.session_state.page == "upload":
    page_upload()
elif st.session_state.page == "analysis":
    page_analysis()
else:
    page_final()
