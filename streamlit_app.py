import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/analyze"


st.set_page_config(page_title="ATS Resume Analyzer")
st.title("ATS Resume Analyzer")
st.write("Paste a resume and a job description, then click Analyze.")

resume_text = st.text_area("Resume", height=220)
job_description = st.text_area("Job Description", height=220)


if st.button("Analyze"):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please fill in both text areas.")
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

            st.subheader("Result")
            st.success(f"Final Score: {final}%")
            st.write(f"Semantic Score: {semantic}%")
            st.write(f"Keyword Score: {keyword}%")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the FastAPI app. Make sure it is running on http://127.0.0.1:8000.")
        except requests.exceptions.RequestException as error:
            st.error(f"API request failed: {error}")
