import os
import io
import re
from typing import Dict, List, Any

from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Extract raw text from PDF/DOCX/others using in-memory bytes."""
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join([para.text for para in doc.paragraphs])
    # Fallback: treat as plain text
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_text_from_path(path: str) -> str:
    """Extract text from a saved file path."""
    with open(path, "rb") as f:
        data = f.read()
    return extract_text_from_bytes(data, path)


def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def parse_resume_with_llm(text: str) -> Dict[str, Any]:
    """Use LLM to extract structured info + keywords from resume text."""
    client = _get_openai_client()
    prompt = (
        "You are an expert resume parser. "
        "Extract concise structured info and focus on skills/keywords. "
        "Return JSON with keys: name, email, phone, location, summary, "
        "education (list of {degree, institution, start, end}), "
        "experience (list of {title, company, start, end, summary}), "
        "skills (list of strings), keywords (list of 5-15 important keywords). "
        "Do not include null/empty fields. Keep strings short."
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text[:12000]},  # cap for safety
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    content = completion.choices[0].message.content
    import json

    try:
        data = json.loads(content or "{}")
    except Exception:
        data = {}
    # Normalize
    data["keywords"] = list({k.strip() for k in data.get("keywords", []) if k})[:30]
    data["skills"] = list({k.strip() for k in data.get("skills", []) if k})[:50]
    return data


def extract_resume_data(data: bytes, filename: str) -> Dict[str, Any]:
    """High-level helper: extract text, call LLM, return structured result."""
    raw_text = extract_text_from_bytes(data, filename)
    cleaned = _clean_text(raw_text)
    llm_data = parse_resume_with_llm(cleaned)
    llm_data["raw_text"] = cleaned[:5000]  # return snippet for debug
    return llm_data

