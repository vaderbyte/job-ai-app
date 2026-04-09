from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello ATS App 🚀"}

@app.get("/analyze")
def analyze(resume: str, job: str):
    resume_words = set(resume.lower().split())
    job_words = set(job.lower().split())

    matched = resume_words & job_words
    missing = job_words - resume_words

    score = int((len(matched) / len(job_words)) * 100) if job_words else 0

    return {
        "match_score": score,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }