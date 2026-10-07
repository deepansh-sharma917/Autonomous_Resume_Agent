from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os, shutil
import pickle
from db import get_db
from utils import emb, cosine_sim, get_fit_level, explain_match
from tools import extract_text_from_file

app = FastAPI(title="Optimized Resume Matching API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class JobMatchRequest(BaseModel):
    job_text: Optional[str] = None
    job_points: Optional[List[str]] = None


# =========================
# Upload Resume
# =========================
@app.post("/upload-resume")
async def upload_resume(resume: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, resume.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    resume_text = extract_text_from_file(file_path)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Failed to extract resume")

    # Create embedding ONCE
    resume_embedding = emb.embed_query(resume_text)

    conn = get_db()
    cursor = conn.cursor()

    # Deactivate previous active resume
    cursor.execute("UPDATE resumes SET is_active = 0 WHERE is_active = 1")

    # Insert new resume as active
    cursor.execute("""
        INSERT INTO resumes (filename, text, embedding, is_active)
        VALUES (?, ?, ?, 1)
    """, (
        resume.filename,
        resume_text,
        pickle.dumps(resume_embedding)
    ))

    conn.commit()
    conn.close()

    return {
        "message": "Resume uploaded successfully"
    }


# =========================
# Match Resume
# =========================
@app.post("/match")
async def match_resume(payload: JobMatchRequest):
    conn = get_db()

    resume = conn.execute("""
        SELECT text, embedding
        FROM resumes
        WHERE is_active = 1
        LIMIT 1
    """).fetchone()

    conn.close()

    if resume is None:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")

    resume_text = resume["text"]
    resume_embedding = pickle.loads(resume["embedding"])

    job_text = payload.job_text
    if not job_text and payload.job_points:
        job_text = "\n".join(payload.job_points)

    if not job_text:
        raise HTTPException(status_code=400, detail="Job text is required")

    job_embedding = emb.embed_query(job_text)

    score = round(cosine_sim(resume_embedding, job_embedding), 2)
    fit_level = get_fit_level(score)
    explanation = explain_match(resume_text, job_text, score)

    return {
        "match_score": score,
        "fit_level": fit_level,
        "explanation": explanation
    }
