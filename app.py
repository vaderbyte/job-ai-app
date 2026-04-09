from collections import Counter
import re

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Resume Analyzer API")


class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str


def tokenize(text: str) -> list[str]:
    """Convert text into simple lowercase words."""
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def calculate_similarity(resume_text: str, job_description: str) -> float:
    """Compare texts with cosine similarity and return a score from 0 to 100."""
    resume_words = tokenize(resume_text)
    job_words = tokenize(job_description)

    if not resume_words or not job_words:
        return 0.0

    resume_counts = Counter(resume_words)
    job_counts = Counter(job_words)

    common_words = set(resume_counts) & set(job_counts)
    dot_product = sum(resume_counts[word] * job_counts[word] for word in common_words)

    resume_length = sum(count * count for count in resume_counts.values()) ** 0.5
    job_length = sum(count * count for count in job_counts.values()) ** 0.5

    if resume_length == 0 or job_length == 0:
        return 0.0

    similarity = dot_product / (resume_length * job_length)
    return round(similarity * 100, 2)


@app.get("/")
def read_root():
    return {"message": "Resume Analyzer API is running"}


@app.post("/analyze")
def analyze_resume(data: AnalyzeRequest):
    score = calculate_similarity(data.resume_text, data.job_description)

    return {
        "similarity_score": score,
        "semantic_score": score,
        "message": "Higher scores mean the resume shares more words with the job description.",
    }
