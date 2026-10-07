from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import numpy as np
import json
from config import OPENAI_API_KEY

emb = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)


def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_fit_level(score: float) -> str:
    if score >= 0.8:
        return "Strong Fit"
    elif score >= 0.6:
        return "Good Fit"
    elif score >= 0.4:
        return "Average Fit"
    else:
        return "Weak Fit"


def explain_match(resume: str, job: str, score: float) -> dict:
    response = llm.invoke(f"""
You are an ATS evaluator.

Return STRICT JSON in this format only:

{{
  "summary": "1–2 lines summary",
  "strengths": ["point1", "point2"],
  "gaps": ["point1", "point2"],
  "recommendations": ["point1", "point2"]
}}

Resume:
{resume}

Job Description:
{job}
""").content.strip()

    return json.loads(response)
