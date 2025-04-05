import streamlit as st
from pathlib import Path
import base64

# Add src to path for importing custom modules
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils.pdf_utils import extract_text_from_pdf
from src.api.grok_client import call_grok_api
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(page_title="Resume Builder", layout="wide")

# --- Style fix for full-width
st.markdown("""
    <style>
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Background audio autoplay (once)
audio_path = Path(__file__).resolve().parent.parent / "src" / "assets" / "voice.mp3"
if audio_path.exists():
    with open(audio_path, "rb") as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode()
    st.components.v1.html(f"""
        <audio autoplay hidden>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """, height=0)
else:
    st.warning(f"Voice file not found at: {audio_path}")

# --- Upload Section ---
st.title("Welcome to Resume Builder")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.markdown("### Uploaded Resume:")
    st.markdown("<div style='width: 100%; display: flex; justify-content: center;'>", unsafe_allow_html=True)
    pdf_viewer(uploaded_file.getvalue(), width="100%", height=900)
    st.markdown("</div>", unsafe_allow_html=True)

    # "Next" button
    col1, col2, col3 = st.columns([1, 6, 1])
    with col3:
        if st.button("Next ➡️"):
            with st.spinner("Analyzing your resume..."):

                # Loading GIF
                gif_path = Path(__file__).resolve().parent.parent/ "src"  / "assets" / "loading.gif"
                if gif_path.exists():
                    st.image(str(gif_path), use_column_width=True)
                else:
                    st.warning("Loading GIF not found.")

                # Extract text and send to API
                pdf_text = extract_text_from_pdf(uploaded_file)
                prompt = "Extract structured details like name, email, skills, etc."
                result = call_grok_api(prompt, pdf_text)

                st.success("Resume parsed successfully!")
                st.subheader("Result:")
                st.json(result)

                # Optional: download result
                st.download_button(
                    label="Download Result",
                    data=str(result).encode(),
                    file_name="parsed_resume.json"
                )
