# Resume Genius: AI-Powered Voice-Based Resume Builder

## 📌 Project Overview
This project is an intelligent resume generator that:
- Analyzes a job description and extracts keywords.
- Auto-fills a sample resume with relevant content.
- Allows interactive voice-based editing using Speech-to-Text.
- Optimizes resumes for ATS (Applicant Tracking Systems).
- Exports final resumes as PDF and sends via email.

## 🎓 Course Information
This project was developed as part of the **Natural Language Processing Final Project** for the course:

- **Course**: NLP (Natural Language Processing)
- **Instructor**: Dr. Amir Jafari
- **Due Date**: Refer to course syllabus
- **Semester**: Spring 2025

## 🧠 Core NLP Concepts Used
- Pretrained Transformers (BERT / SBERT)
- Keyword Extraction & Matching
- Cosine Similarity (TF-IDF embeddings)
- Rule-Based Modifications
- Voice Interaction using Whisper / SpeechRecognition
- Resume Scoring for ATS optimization

## 🧰 Tech Stack
- `Python`, `Streamlit` (UI), `SpeechRecognition` / `Whisper`
- `sentence-transformers`, `spaCy`, `Scikit-learn`
- `pdfkit` / `python-docx` for PDF generation
- `smtplib` / `Flask-Mail` / `SendGrid` for email

### 📁 Project Structure

```plaintext
Final-Project-GroupX/
├── Group-Proposal/
│   └── group_proposal.pdf
│
├── Final-Group-Project-Report/
│   └── final_report.pdf
│
├── Final-Group-Presentation/
│   └── presentation.pdf
│
├── Code/
│   ├── app.py
│   ├── resume_generator.py
│   ├── voice_input.py
│   ├── ats_optimizer.py
│   ├── email_sender.py
│   └── README.md
│
└── README.md
```

## 📬 Output
- 📄 Resumes optimized for ATS
- 📧 Sent to user’s email
- 🗣️ Editable through voice prompts

## 👥 Team
This is a group project. Please refer to the individual report for each member's contributions.

## 📎 License
MIT License
