import os
import json
from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from openrouter import OpenRouter
from dotenv import load_dotenv

# ----------------------
# LOAD ENV
# ----------------------
load_dotenv()

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ SAFE API KEY LOADING
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY not found in environment variables")

client = OpenRouter(api_key=api_key)


class ATSRequest(BaseModel):
    resume: str
    job: str


# ----------------------
# SEMANTIC SCORE
# ----------------------
def semantic_score(resume: str, jd: str) -> float:
    emb1 = model.encode(resume, convert_to_tensor=True)
    emb2 = model.encode(jd, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(score * 100, 2)


# ----------------------
# LLM ANALYSIS
# ----------------------
def llm_analysis(resume: str, jd: str) -> Dict:
    prompt = f"""
You are an ATS evaluator.

Evaluate the resume against the job description.

Return STRICT JSON:
- strengths
- gaps
- improvement_points
- keyword_score (0-100)

Rules:
- No generic words
- Focus on capabilities
- Be concise

Resume:
{resume}

Job Description:
{jd}
"""

    try:
        response = client.chat.send(
            model="openai/gpt-oss-120b:free",
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content
        data = json.loads(content)

    except Exception as e:
        print("LLM ERROR:", e)
        data = {
            "strengths": [],
            "gaps": [],
            "improvement_points": [],
            "keyword_score": 0
        }

    return data


# ----------------------
# FINAL SCORE
# ----------------------
def final_score(semantic: float, keyword: float) -> float:
    return round((0.6 * semantic) + (0.4 * keyword), 2)


# ----------------------
# MAIN API
# ----------------------
@app.post("/analyze")
def analyze(data: ATSRequest):
    resume = data.resume
    jd = data.job

    sem = semantic_score(resume, jd)
    llm_data = llm_analysis(resume, jd)

    keyword = llm_data.get("keyword_score", 0)
    final = final_score(sem, keyword)

    return {
        "final_score": final,
        "semantic_score": sem,
        "keyword_score": keyword,
        "strengths": llm_data.get("strengths", []),
        "gaps": llm_data.get("gaps", []),
        "improvement_points": llm_data.get("improvement_points", [])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
