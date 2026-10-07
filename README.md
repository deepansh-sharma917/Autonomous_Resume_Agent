# 🤖 Autonomous Resume Agent

An AI-powered **Resume–Job Description Matching Agent** built with **FastAPI, OpenAI Embeddings, SQLite, and GPT-4o-mini**.

The application allows users to upload a resume in **PDF or DOCX format**, automatically extracts its content, generates and stores an embedding, and compares the resume against a given job description.

The agent provides:

* 📄 Resume upload and text extraction
* 🧠 Resume embeddings using `text-embedding-3-small`
* 🔎 Semantic similarity between resume and job description
* 📊 Match score and fit classification
* 🤖 LLM-powered explanation of the match
* 💪 Strengths identified from the resume
* ❌ Skill/experience gaps
* 💡 Recommendations for improving the resume
* 💾 Persistent resume storage using SQLite
* ⚡ REST API using FastAPI

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │       Client         │
                    │ Swagger / Postman    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │       app.py         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
   ┌───────────────────┐               ┌──────────────────┐
   │ Resume Processing │               │  Job Description │
   │                   │               │                  │
   │ PDF / DOCX        │               │ job_text /       │
   │ Text Extraction   │               │ job_points       │
   └─────────┬─────────┘               └────────┬─────────┘
             │                                  │
             ▼                                  ▼
   ┌───────────────────┐               ┌──────────────────┐
   │ OpenAI Embedding  │               │ OpenAI Embedding │
   │ text-embedding-   │               │ text-embedding-  │
   │ 3-small           │               │ 3-small          │
   └─────────┬─────────┘               └────────┬─────────┘
             │                                  │
             ▼                                  ▼
   ┌───────────────────┐               ┌──────────────────┐
   │ SQLite            │               │ Cosine Similarity│
   │ Resume + Vector   │               │                  │
   └───────────────────┘               └────────┬─────────┘
                                                │
                                                ▼
                                     ┌────────────────────┐
                                     │   Fit Evaluation   │
                                     │ Strong / Good /    │
                                     │ Average / Weak     │
                                     └─────────┬──────────┘
                                               │
                                               ▼
                                     ┌────────────────────┐
                                     │ GPT-4o-mini        │
                                     │ Match Explanation  │
                                     └─────────┬──────────┘
                                               │
                                               ▼
                                     ┌────────────────────┐
                                     │ JSON API Response  │
                                     └────────────────────┘
```

---

# 📁 Project Structure

```text
autonomous-resume-agent/
│
├── app.py
├── config.py
├── db.py
├── tools.py
├── utils.py
│
├── uploads/
│   └── uploaded resumes
│
├── data.db
├── .env
├── requirements.txt
└── README.md
```

### `app.py`

Main FastAPI application.

Responsibilities:

* Resume upload
* Resume text extraction
* Resume embedding generation
* Resume storage
* Job description processing
* Resume–JD similarity calculation
* Fit classification
* AI-generated explanation

---

### `config.py`

Loads environment variables.

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

The OpenAI API key is loaded from `.env`.

---

### `db.py`

Handles SQLite database operations.

The application creates a `resumes` table:

```text
resumes
├── id
├── filename
├── text
├── embedding
├── is_active
└── created_at
```

Only one resume is maintained as the **active resume**.

When a new resume is uploaded:

```text
Previous Resume
      │
      ▼
is_active = 0

New Resume
      │
      ▼
is_active = 1
```

---

### `tools.py`

Responsible for extracting text from uploaded files.

Supported formats:

* PDF
* DOCX

PDF extraction uses:

```python
PdfReader
```

DOCX extraction uses:

```python
docx2txt
```

---

### `utils.py`

Contains the AI and matching functionality.

It initializes:

```python
OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

and:

```python
ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
```

It also provides:

* `cosine_sim()`
* `get_fit_level()`
* `explain_match()`

---

# ⚙️ How the Agent Works

## 1. Upload Resume

The user sends a PDF or DOCX resume to:

```http
POST /upload-resume
```

Example:

```bash
curl -X POST \
  http://127.0.0.1:8000/upload-resume \
  -F "resume=@resume.pdf"
```

The system:

```text
Resume
   ↓
File Upload
   ↓
Text Extraction
   ↓
OpenAI Embedding
   ↓
SQLite Storage
```

The embedding is generated **once during upload** rather than every time the resume is matched.

This avoids unnecessary embedding API calls for the same resume.

---

# 2. Provide Job Description

The `/match` endpoint accepts either:

### Complete Job Description

```json
{
  "job_text": "We are looking for a Python developer with experience in FastAPI, PostgreSQL, Docker and AWS."
}
```

or individual job points:

```json
{
  "job_points": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "AWS"
  ]
}
```

If `job_points` is provided, the system combines them:

```text
Python
FastAPI
PostgreSQL
Docker
AWS
```

into a single text representation.

---

# 3. Generate Job Embedding

The job description is converted into an embedding using:

```text
text-embedding-3-small
```

Unlike the resume embedding, the job embedding is generated when the matching request is made because each job description can be different.

---

# 4. Calculate Semantic Similarity

The application compares:

```text
Resume Embedding
       │
       │
       ▼
Cosine Similarity
       ▲
       │
       │
Job Embedding
```

The cosine similarity is calculated using:

```python
def cosine_sim(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )
```

The resulting score is rounded to two decimal places.

Example:

```text
0.86
```

---

# 5. Determine Fit Level

The system converts the similarity score into a human-readable category.

|         Score | Fit Level      |
| ------------: | -------------- |
|     `>= 0.80` | 🟢 Strong Fit  |
| `0.60 - 0.79` | 🟢 Good Fit    |
| `0.40 - 0.59` | 🟡 Average Fit |
|      `< 0.40` | 🔴 Weak Fit    |

For example:

```text
Match Score: 0.84
Fit Level: Strong Fit
```

---

# 6. Generate AI Explanation

The application sends the resume and job description to GPT-4o-mini.

The LLM evaluates:

### Strengths

Skills and experience that align with the job.

### Gaps

Skills, technologies, or experience missing from the resume.

### Recommendations

Suggestions for improving the candidate's resume or fit.

The expected response format is:

```json
{
  "summary": "The candidate has strong experience in Python and backend development.",
  "strengths": [
    "Strong Python experience",
    "Experience building FastAPI applications"
  ],
  "gaps": [
    "Limited AWS experience"
  ],
  "recommendations": [
    "Highlight cloud deployment experience"
  ]
}
```

---

# 🚀 API Endpoints

## `POST /upload-resume`

Uploads and processes a resume.

### Request

```text
multipart/form-data
```

Field:

```text
resume
```

Supported:

```text
.pdf
.docx
```

### Example

```bash
curl -X POST \
  http://127.0.0.1:8000/upload-resume \
  -F "resume=@my_resume.pdf"
```

### Response

```json
{
  "message": "Resume uploaded successfully"
}
```

---

# `POST /match`

Matches the active resume against a job description.

### Request — `job_text`

```json
{
  "job_text": "Looking for a Data Scientist with Python, SQL, Machine Learning, NLP and FastAPI experience."
}
```

### Request — `job_points`

```json
{
  "job_points": [
    "Python",
    "SQL",
    "Machine Learning",
    "NLP",
    "FastAPI"
  ]
}
```

### Example Response

```json
{
  "match_score": 0.82,
  "fit_level": "Strong Fit",
  "explanation": {
    "summary": "The resume aligns strongly with the Data Scientist position.",
    "strengths": [
      "Strong Python and machine learning experience",
      "Experience with NLP applications"
    ],
    "gaps": [
      "Limited production SQL experience"
    ],
    "recommendations": [
      "Highlight SQL projects and database experience"
    ]
  }
}
```

---

# 🧪 Error Handling

### No resume uploaded

```http
404 Not Found
```

Response:

```json
{
  "detail": "No resume uploaded yet"
}
```

---

### Missing Job Description

```http
400 Bad Request
```

Response:

```json
{
  "detail": "Job text is required"
}
```

---

### Empty Resume

```http
400 Bad Request
```

Response:

```json
{
  "detail": "Failed to extract resume"
}
```

---

### Unsupported File

The application raises:

```text
ValueError: Unsupported file format
```

Supported formats are currently:

```text
PDF
DOCX
```

---

# 🔧 Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd autonomous-resume-agent
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Dependencies

Create `requirements.txt`:

```text
fastapi
uvicorn
python-multipart
python-dotenv
pypdf
docx2txt
numpy
langchain-openai
openai
```

Install:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

Do **not** commit `.env` to Git.

Add it to `.gitignore`:

```text
.env
venv/
__pycache__/
uploads/
data.db
```

---

# ▶️ Run the Application

Start FastAPI using:

```bash
uvicorn app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📚 Swagger Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can test:

```text
POST /upload-resume
POST /match
```

directly from Swagger UI.

---

# 🔄 Complete Workflow

```text
             USER
              │
              ▼
       Upload Resume
              │
              ▼
       PDF / DOCX Parser
              │
              ▼
       Extract Resume Text
              │
              ▼
      OpenAI Embedding Model
      text-embedding-3-small
              │
              ▼
       Store in SQLite
              │
              │
              │
       User submits JD
              │
              ▼
       Generate JD Embedding
              │
              ▼
      Cosine Similarity
              │
              ▼
        Match Score
              │
              ▼
        Fit Classification
              │
              ▼
          GPT-4o-mini
              │
              ▼
     ┌─────────────────────┐
     │ Summary             │
     │ Strengths           │
     │ Gaps                │
     │ Recommendations     │
     └─────────────────────┘
              │
              ▼
          JSON Response
```

---

# 🧠 Why Embeddings?

Traditional keyword matching can fail when the resume and job description use different terminology.

For example:

```text
Resume:
"Built REST APIs using FastAPI"

Job:
"Experience developing backend services using Python web frameworks"
```

A simple keyword search may not recognize this as a strong relationship.

Embeddings represent the text as vectors that capture semantic information.

Therefore:

```text
Resume Meaning
      ↓
Embedding Vector

Job Meaning
      ↓
Embedding Vector

       ↓

Semantic Similarity
```

This allows the system to perform **semantic resume matching** rather than simple keyword matching.

---

# 🤖 AI Components

| Component         | Technology                      |
| ----------------- | ------------------------------- |
| API               | FastAPI                         |
| Language          | Python                          |
| Resume Parsing    | PyPDF + docx2txt                |
| Embeddings        | OpenAI `text-embedding-3-small` |
| LLM               | OpenAI `gpt-4o-mini`            |
| Similarity        | Cosine Similarity               |
| Database          | SQLite                          |
| ORM               | None                            |
| API Documentation | FastAPI Swagger                 |
| Configuration     | python-dotenv                   |

---

# ⚡ Optimization

The system intentionally generates the resume embedding only once.

### Without optimization

```text
Every /match request
        ↓
Generate Resume Embedding
        ↓
Generate Job Embedding
        ↓
Calculate similarity
```

This would repeatedly call the embedding API for the same resume.

### Current implementation

```text
Upload Resume
      ↓
Generate Resume Embedding
      ↓
Store Embedding
      ↓
        /match
           ↓
Load Resume Embedding
           +
Generate Job Embedding
           ↓
Calculate Similarity
```

This reduces unnecessary API calls and improves matching performance.

---

# 🔒 Current Limitations

This is currently a lightweight implementation and intentionally avoids unnecessary infrastructure.

Current limitations include:

* SQLite instead of PostgreSQL
* Embeddings stored as serialized BLOBs
* Single active resume
* No authentication
* No user accounts
* No vector database
* No resume chunking
* No skill extraction pipeline
* No job history
* No batch job matching
* No frontend UI
* No asynchronous background processing
* LLM JSON parsing assumes valid JSON output
* Cosine similarity provides an overall semantic score but does not independently verify individual skills

---

# 🚀 Future Improvements

The project can be extended into a more production-oriented **Autonomous Resume Agent**.

### 1. Skill Extraction

Extract structured skills from the resume:

```json
{
  "technical_skills": [
    "Python",
    "FastAPI",
    "LangChain",
    "PostgreSQL"
  ],
  "experience": 3,
  "education": [
    "M.Tech Data Science"
  ]
}
```

---

### 2. Job Requirement Extraction

Convert a job description into structured requirements:

```json
{
  "required_skills": [
    "Python",
    "FastAPI"
  ],
  "preferred_skills": [
    "Docker",
    "AWS"
  ],
  "experience_required": 2
}
```

---

### 3. Hybrid Matching

Instead of relying only on semantic similarity:

```text
Final Score
    │
    ├── Semantic Similarity
    ├── Skill Match
    ├── Experience Match
    ├── Education Match
    └── Keyword Match
```

For example:

```text
Final Score =
40% Semantic Similarity
30% Skill Match
20% Experience Match
10% Education Match
```

This would make the scoring more interpretable.

---

### 4. Resume Improvement Agent

The agent could automatically identify missing requirements and suggest resume modifications.

Example:

```text
Job requires:
AWS

Resume:
No AWS experience detected.

Recommendation:
Add relevant AWS project/deployment experience if applicable.
```

---

### 5. Multiple Resume Support

Instead of maintaining only one active resume:

```text
Resume 1 → Data Scientist
Resume 2 → AI Engineer
Resume 3 → Backend Engineer
```

The agent could automatically select the most relevant resume for a job.

---

### 6. Vector Database

For larger-scale implementations, resume and job embeddings could be stored in a vector database such as:

```text
Pinecone
PostgreSQL + pgvector
Qdrant
FAISS
```

This would enable efficient semantic retrieval across many resumes and job descriptions.

---

### 7. Agentic Workflow

The next evolution could be:

```text
Job Description
       ↓
Requirement Extraction
       ↓
Resume Retrieval
       ↓
Semantic Matching
       ↓
Skill Gap Analysis
       ↓
Resume Optimization
       ↓
ATS Evaluation
       ↓
Final Recommendation
```

This transforms the project from a simple similarity API into an **agentic resume optimization system**.

---

# 🎯 Use Cases

This project can be used for:

* Resume–JD matching
* ATS-style resume analysis
* Job application prioritization
* Skill-gap analysis
* Resume improvement
* Candidate screening
* AI-powered career tools
* Automated job application workflows

---

# 💡 Key Technical Concepts Demonstrated

This project demonstrates practical experience with:

```text
FastAPI
REST APIs
LLM Integration
Embeddings
Semantic Search
Cosine Similarity
Prompt Engineering
Structured LLM Output
Document Processing
SQLite
API Design
Environment Configuration
AI-based Recommendation Systems
```

---

# 📌 Project Summary

**Autonomous Resume Agent** is an AI-powered resume matching system that combines **semantic embeddings and LLM reasoning** to evaluate how well a resume matches a job description.

Instead of relying purely on keyword matching, the system uses embeddings to measure semantic similarity and an LLM to provide an interpretable explanation containing:

```text
Match Score
     +
Fit Level
     +
Strengths
     +
Gaps
     +
Recommendations
```

The architecture is intentionally lightweight while providing a foundation for extending the project into a production-grade **AI/Agentic Resume Optimization Platform**.

---

## 👨‍💻 Technology Stack

```text
Python
FastAPI
OpenAI API
LangChain OpenAI
GPT-4o-mini
text-embedding-3-small
SQLite
NumPy
PyPDF
docx2txt
Uvicorn
```

---

## ⭐ Future Vision

```text
                 ┌─────────────────────┐
                 │   Job Description    │
                 └──────────┬──────────┘
                            ↓
                  Requirement Agent
                            ↓
                 Resume Retrieval Agent
                            ↓
                  Matching Agent
                            ↓
                 Skill Gap Agent
                            ↓
              Resume Optimization Agent
                            ↓
                    ATS Evaluation
                            ↓
                 Application Decision
```

The long-term goal is to evolve the current API into an **autonomous AI career agent** capable of analyzing jobs, selecting the best resume version, identifying gaps, recommending improvements, and helping prioritize job applications.
