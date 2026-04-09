from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello ATS App 🚀"}

@app.get("/analyze")
def analyze(resume: str, job: str):
    resume_words = set(resume.lower().split())
    job_words = set(job.lower().split())

    if not job_words:
        return {"error": "Job description is empty"}

    matched = resume_words.intersection(job_words)
    missing = job_words.difference(resume_words)

    score = round((len(matched) / len(job_words)) * 100, 2)

    return {
        "match_score": score,
        "matched_count": len(matched),
        "total_keywords": len(job_words),
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }