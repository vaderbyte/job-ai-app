import re
from pydantic import BaseModel
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

class InputData(BaseModel):
    resume: str
    job: str

@app.get("/")
def read_root():
    return {"message": "Hello ATS App 🚀"}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()

    stopwords = {
        "the","and","is","in","to","of","for","on","with","a","an",
        "about","what","will","our","you","your","we","are","as",
        "by","be","this","that","or","from","at","it","into","across",
        "using","use","used","based","within","through","over",
        "include","including","required","preferred"
    }

    # 🔥 NEW: filter short + useless words
    clean_words = [
        word for word in words
        if word not in stopwords and len(word) > 3
    ]

    return set(clean_words)

@app.post("/analyze")
def analyze(data: InputData):
    resume = data.resume
    job = data.job

    if not resume or not job:
        return {"error": "Missing input"}

    # ---------- KEYWORD SCORE ----------
    resume_words = clean_text(resume)
    job_words = clean_text(job)

    matched = resume_words.intersection(job_words)

    keyword_score = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

    # ---------- SEMANTIC SCORE ----------
    clean_resume = " ".join(resume_words)
    clean_job = " ".join(job_words)

    resume_embedding = model.encode([clean_resume])
    job_embedding = model.encode([clean_job])

    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    semantic_score = round(float(similarity) * 100, 2)

    # ---------- FINAL SCORE ----------
    final_score = round((0.5 * keyword_score) + (0.5 * semantic_score), 2)

    return {
        "semantic_score": semantic_score,
        "keyword_score": keyword_score,
        "final_score": final_score,
        "matched_keywords": list(matched),
        "missing_keywords": list(job_words - resume_words)
    }