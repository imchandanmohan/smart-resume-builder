import streamlit as st
import base64
import time
from pathlib import Path

# Page config
st.set_page_config(page_title="Smart Resume Builder", layout="wide")

# Custom CSS
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
    .profile-tile {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background-color: #222;
        color: white;
        text-align: center;
    }
    .stTextArea textarea {
        border: 1px solid Red !important;
    }
</style>
""", unsafe_allow_html=True)

# Paths
base_audio_path = Path(__file__).resolve().parent.parent / "src/assets/agentvoice/prerecorded/v2_en/en_speaker_6"
general_audio_path = Path(__file__).resolve().parent.parent / "src/assets/agentvoice/prerecorded/generalsounds"

welcome_path = base_audio_path / "Welcome.mp3"
confres_path = base_audio_path / "ConfRes.mp3"
confdes_path = base_audio_path / "ConfDes.mp3"
ringtone_path = general_audio_path / "cellphone-ringing.mp3"

# === JS Audio Playback for Welcome → Resume Upload Chain === #
if welcome_path.exists() and confres_path.exists():
    with open(welcome_path, "rb") as f:
        welcome_b64 = base64.b64encode(f.read()).decode()
    with open(confres_path, "rb") as f:
        confres_b64 = base64.b64encode(f.read()).decode()

    st.components.v1.html(f"""
    <audio id="welcome" autoplay hidden>
        <source src="data:audio/mp3;base64,{welcome_b64}" type="audio/mp3">
    </audio>
    <audio id="confres" hidden>
        <source src="data:audio/mp3;base64,{confres_b64}" type="audio/mp3">
    </audio>
    <script>
        const welcome = document.getElementById("welcome");
        const confres = document.getElementById("confres");
        welcome.onended = function() {{
            if (sessionStorage.getItem("resumeUploaded") === "true") {{
                confres.play();
            }}
        }};
    </script>
    """, height=0)

# Header
st.markdown("""
<div class="header">
    <h1 style="margin:0;">Smart Resume Builder</h1>
    <p style="margin:0;">Upload your resume and job description for analysis</p>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns(2, gap="large")

# Resume Upload
with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file and "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = True
        st.components.v1.html("""
            <script> sessionStorage.setItem("resumeUploaded", "true"); </script>
        """, height=0)

    if uploaded_file:
        with st.expander("View Resume", expanded=True):
            pdf_bytes = uploaded_file.read()
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="700" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

# Job Description Input
with col2:
    st.subheader("📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=1000,
        placeholder="Paste the full job description you're applying for...",
        label_visibility="collapsed"
    )

    if job_description and "description_confirmed" not in st.session_state:
        st.session_state.description_confirmed = True
        with st.spinner("Processing job description..."):
            time.sleep(6)

        if confdes_path.exists():
            with open(confdes_path, "rb") as f:
                confdes_b64 = base64.b64encode(f.read()).decode()

            st.components.v1.html(f"""
                <audio autoplay hidden>
                    <source src="data:audio/mp3;base64,{confdes_b64}" type="audio/mp3">
                </audio>
            """, height=0)

        st.session_state.show_profiles = True

# Show Profiles
if st.session_state.get("show_profiles"):
    st.markdown("### Candidate Profiles")
    profile_col1, profile_col2, profile_col3 = st.columns(3)

    def play_ringtone_and_redirect():
        if not ringtone_path.exists():
            st.error("Ringtone file not found")
            return

        with open(ringtone_path, "rb") as f:
            ringtone_b64 = base64.b64encode(f.read()).decode()

        st.components.v1.html(f"""
            <audio id="ringtone" autoplay hidden>
                <source src="data:audio/mp3;base64,{ringtone_b64}" type="audio/mp3">
            </audio>
            <script>
                const audio = document.getElementById("ringtone");
                audio.play();
                setTimeout(function() {{
                    window.location.href = "/Resume_Builder";
                }}, 10000);
            </script>
        """, height=0)


    if profile_col1.button("🔎 John Smith"):
        play_ringtone_and_redirect()

    if profile_col2.button("🔎 Sarah Johnson"):
        play_ringtone_and_redirect()

    if profile_col3.button("🔎 Michael Chen"):
        play_ringtone_and_redirect()

# Status + Analyze Button
st.markdown("---")
status_col, btn_col = st.columns([3, 1])

with status_col:
    if uploaded_file:
        st.info("✅ Resume uploaded successfully")
    if job_description:
        st.info("✅ Job description ready for analysis")

with btn_col:
    if st.button("Analyze ➡️", type="primary", use_container_width=True):
        with st.spinner("Analyzing your resume..."):
            time.sleep(1)
            st.toast("Starting analysis...", icon="🔍")
            time.sleep(2)
            st.toast("Matching your skills to the job...", icon="🎙️")
            time.sleep(1)
            st.success("Analysis complete!")

            st.subheader("Results")
            st.json({
                "match_score": "85%",
                "key_skills": ["Python", "Streamlit", "Data Analysis"],
                "suggestions": ["Highlight more project experience", "Add certification section"]
            })
