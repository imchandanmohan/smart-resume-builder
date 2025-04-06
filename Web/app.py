import streamlit as st
import random
import base64

# Configure page
st.set_page_config(page_title="Resume Builder", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .header {
        background-color: White;
        color: Black;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid Red;
    }
    .resume-container {
        border: 1px solid Red;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .profile-tile {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background-color: #222;
        color: white;
        text-align: center;
    }
    .next-btn {
        float: right;
        margin-top: 1rem;
    }
    .stTextArea textarea {
        border: 1px solid Red !important;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header">
    <h1 style="margin:0;">Smart Resume Builder</h1>
    <p style="margin:0;">Upload your resume and job description for analysis</p>
</div>
""", unsafe_allow_html=True)

# Main Content - Two Columns
col1, col2 = st.columns(2, gap="large")

# Left Column - Resume Upload & Preview
with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with st.expander("View Resume", expanded=True):
            # Save the PDF bytes
            pdf_bytes = uploaded_file.read()

            # Encode to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

# Right Column - Job Description
with col2:
    st.subheader("📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=1000,
        placeholder="Paste the full job description you're applying for..."
    )

# Profile Tiles Section
st.markdown("### Candidate Profiles")
profile_col1, profile_col2, profile_col3 = st.columns(3)

with profile_col1:
    st.markdown("""
    <div class="profile-tile">
        <h3>John Smith</h3>
        <p>Age: 28</p>
        <p>Experience: 5 years</p>
        <p>Skills: Python, Data Analysis</p>
    </div>
    """, unsafe_allow_html=True)

with profile_col2:
    st.markdown("""
    <div class="profile-tile">
        <h3>Sarah Johnson</h3>
        <p>Age: 35</p>
        <p>Experience: 10 years</p>
        <p>Skills: Machine Learning, SQL</p>
    </div>
    """, unsafe_allow_html=True)

with profile_col3:
    st.markdown("""
    <div class="profile-tile">
        <h3>Michael Chen</h3>
        <p>Age: 24</p>
        <p>Experience: 2 years</p>
        <p>Skills: Web Development, JavaScript</p>
    </div>
    """, unsafe_allow_html=True)

# Bottom Section - Status and Actions
st.markdown("---")
status_col, btn_col = st.columns([3, 1])

with status_col:
    if uploaded_file:
        st.info("✅ Resume uploaded successfully")
    if job_description:
        st.info("✅ Job description ready for analysis")

