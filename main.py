import re
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/")
def read_root():
    return {"message": "Hello ATS App 🚀"}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    words = text.split()

    stopwords = {
        "the", "and", "is", "in", "to", "of", "for", "on", "with", "a", "an"
    }

    return set(word for word in words if word not in stopwords)


@app.get("/analyze")
def analyze(resume: str, job: str):
    if not resume or not job:
        return {"error": "Missing input"}

    clean_resume = " ".join(clean_text(resume))
    clean_job = " ".join(clean_text(job))

    resume_embedding = model.encode([clean_resume])
    job_embedding = model.encode([clean_job])

    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]

    return {
        "semantic_score": round(float(similarity) * 100, 2)
    }