import streamlit as st

st.set_page_config(page_title="Resume Builder", layout="wide")

# Sidebar
st.sidebar.title("Resume Builder")
st.sidebar.markdown("Navigate through the pages to build your resume.")

# Main content
st.title("Welcome to Resume Builder")

st.subheader("Upload your existing resume or start fresh")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

st.markdown("### Or")

if st.button("Start as New User"):
    st.success("Navigate to 'Resume Builder' page to begin.")
