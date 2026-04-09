import requests
import streamlit as st
import fitz  # PyMuPDF

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="ATS Resume Analyzer")
st.title("ATS Resume Analyzer")
st.write("Upload a resume or paste text, then add a job description and click Analyze.")

# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ---------- INPUT ----------
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

resume_text = ""

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)
    st.success("Resume uploaded successfully!")
    st.write(f"Extracted characters: {len(resume_text)}")
else:
    resume_text = st.text_area("Or paste Resume", height=220)

job_description = st.text_area("Job Description", height=220)

# ---------- ANALYZE BUTTON ----------
if st.button("Analyze"):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please fill in both fields.")
    else:
        try:
            response = requests.post(
                API_URL,
                json={
                    "resume": resume_text,
                    "job": job_description,
                },
                timeout=10,
            )

            response.raise_for_status()
            result = response.json()

            semantic = result.get("semantic_score")
            keyword = result.get("keyword_score")
            final = result.get("final_score")

            # ---------- OUTPUT ----------
            st.subheader("Result")
            st.success(f"Final Score: {final}%")

            col1, col2 = st.columns(2)
            col1.metric("Semantic Score", f"{semantic}%")
            col2.metric("Keyword Score", f"{keyword}%")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the FastAPI app. Make sure it is running on http://127.0.0.1:8000.")
        except requests.exceptions.RequestException as error:
            st.error(f"API request failed: {error}")