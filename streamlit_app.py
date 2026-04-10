import requests
import streamlit as st
import fitz  # PyMuPDF

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="ATS Resume Analyzer", layout="wide")
st.title("📄 ATS Resume Analyzer")
st.write("Upload your resume, paste a job description, and get intelligent ATS-style feedback.")

# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ---------- INPUT LAYOUT ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📎 Resume Input")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    resume_text = ""

    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)
        st.success("Resume uploaded successfully!")
        st.caption(f"Extracted characters: {len(resume_text)}")
    else:
        resume_text = st.text_area("Or paste Resume", height=300)

with col2:
    st.subheader("🧾 Job Description")
    job_description = st.text_area("Paste Job Description", height=300)

# ---------- ANALYZE BUTTON ----------
st.markdown("---")

if st.button("🚀 Analyze Resume"):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please provide both resume and job description.")
    else:
        with st.spinner("Analyzing with AI..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "resume": resume_text,
                        "job": job_description,
                    },
                    timeout=60,
                )

                response.raise_for_status()
                result = response.json()

                semantic = result.get("semantic_score", 0)
                keyword = result.get("keyword_score", 0)
                final = result.get("final_score", 0)

                strengths = result.get("strengths", [])
                gaps = result.get("gaps", [])
                improvements = result.get("improvement_points", [])

                # ---------- OUTPUT ----------
                st.markdown("## 📊 Results")

                st.progress(int(final))
                st.success(f"Final ATS Score: {final}%")

                col1, col2, col3 = st.columns(3)
                col1.metric("🧠 Semantic Match", f"{semantic}%")
                col2.metric("🤖 AI Match Score", f"{keyword}%")
                col3.metric("⭐ Overall Score", f"{final}%")

                st.markdown("---")

                # ---------- INSIGHTS ----------
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🟢 Strengths")
                    if strengths:
                        for s in strengths:
                            st.markdown(f"- {s}")
                    else:
                        st.info("No strong strengths identified.")

                with col2:
                    st.subheader("🔴 Gaps")
                    if gaps:
                        for g in gaps:
                            st.markdown(f"- {g}")
                    else:
                        st.success("No major gaps detected.")

                # ---------- IMPROVEMENTS ----------
                if improvements:
                    st.markdown("---")
                    st.subheader("💡 How to Improve Your Resume")

                    for imp in improvements:
                        st.markdown(f"👉 {imp}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to backend. Ensure FastAPI is running.")
            except requests.exceptions.RequestException as error:
                st.error(f"API request failed: {error}")
