from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import json
import os
import re
import urllib.request
from html import unescape

from utils.curriculum import extract_job_details_from_cv


_STOPWORDS = {
    "a",
    "about",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "we",
    "with",
    "you",
    "your",
}


def _clean_html_to_text(html_text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_job_description(url: str, timeout: int = 15) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "automatic-resume/0.1",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        charset_match = re.search(r"charset=([\w-]+)", content_type, re.IGNORECASE)
        encoding = charset_match.group(1) if charset_match else "utf-8"
        raw = response.read()
    html_text = raw.decode(encoding, errors="ignore")
    return _clean_html_to_text(html_text)


def _normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def _extract_skill_candidates(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9\+\#\.-]{1,}", text)
    candidates = []
    for token in tokens:
        lowered = token.lower()
        if lowered in _STOPWORDS:
            continue
        if len(lowered) < 2:
            continue
        candidates.append(token)
    return candidates


def _call_openai_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.2,
    max_output_tokens: int = 800,
) -> Dict[str, object]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}],
            },
        ],
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8", errors="ignore")
    parsed = json.loads(raw)

    output_text = ""
    for item in parsed.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                output_text += content.get("text", "")

    output_text = output_text.strip()
    if not output_text:
        raise ValueError("OpenAI response is empty")

    return json.loads(output_text)


def _extract_skills_with_llm(job_text: str, model: str) -> List[str]:
    system_prompt = "Extract skills and technologies from job descriptions."
    user_prompt = (
        "Return JSON only with a single key 'skills' as a list of short skill names. "
        "Do not include duplicates.\n\nJob description:\n" + job_text
    )
    data = _call_openai_json(system_prompt, user_prompt, model=model)
    skills = data.get("skills", [])
    if not isinstance(skills, list):
        return []
    return [str(skill).strip() for skill in skills if str(skill).strip()]


def extract_skills_from_job_description(
    job_text: str,
    llm_assist: bool = True,
    model: str = "gpt-4.1-mini",
) -> List[str]:
    candidates = _extract_skill_candidates(job_text)
    if llm_assist:
        llm_skills = _extract_skills_with_llm(job_text, model=model)
        combined = candidates + llm_skills
    else:
        combined = candidates

    seen = set()
    ordered = []
    for skill in combined:
        key = _normalize_skill(skill)
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(skill)
    return ordered


def compute_skill_gap(
    job_skills: List[str],
    applicant_skills: List[str],
) -> Tuple[List[str], List[str]]:
    applicant_map = {_normalize_skill(skill): skill for skill in applicant_skills}
    matching = []
    missing = []
    for skill in job_skills:
        key = _normalize_skill(skill)
        if not key:
            continue
        if key in applicant_map:
            matching.append(applicant_map[key])
        else:
            missing.append(skill)
    return matching, missing


def rewrite_cv_with_openai(
    cv_parts: Dict[str, object],
    job_description: str,
    relevant_skills: List[str],
    missing_skills: List[str],
    max_skills: int = 12,
    output_format: str = "markdown",
    model: str = "gpt-4.1-mini",
) -> str:
    system_prompt = (
        "You are a resume editor. Rewrite the resume to better match the job description. "
        "Do not add skills, roles, or achievements that are not present in the input. "
        "Only rephrase or reorder content."
    )

    trimmed_skills = relevant_skills[:max_skills]

    user_prompt = (
        "Return JSON only with a single key 'resume' whose value is the rewritten resume in "
        + output_format
        + ". Use these sections: Title, About Me, Experience, Skills. "
        "For Experience, keep each entry header unchanged and rewrite bullet points only. "
        "Only include skills from the provided relevant skills list. "
        "Do not mention missing skills.\n\n"
        "Job description:\n"
        + job_description
        + "\n\n"
        "Relevant skills:\n"
        + ", ".join(trimmed_skills)
        + "\n\n"
        "Missing skills (do not mention):\n"
        + ", ".join(missing_skills)
        + "\n\n"
        "Resume content:\n"
        + json.dumps(cv_parts, ensure_ascii=True)
    )

    data = _call_openai_json(system_prompt, user_prompt, model=model, max_output_tokens=1200)
    rewritten = data.get("resume")
    if isinstance(rewritten, str) and rewritten.strip():
        return rewritten.strip()

    text = data.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()

    raise ValueError("OpenAI response did not include a resume")


def tailor_resume_from_url(
    job_url: str,
    cv: Union[str, os.PathLike],
    max_skills: int = 12,
    model: str = "gpt-4.1-mini",
    output_format: str = "markdown",
) -> Dict[str, object]:
    job_text = fetch_job_description(job_url)
    job_skills = extract_skills_from_job_description(job_text, llm_assist=True, model=model)
    cv_parts = extract_job_details_from_cv(cv)

    matching, missing = compute_skill_gap(job_skills, cv_parts.get("skills", []))
    rewritten = rewrite_cv_with_openai(
        cv_parts=cv_parts,
        job_description=job_text,
        relevant_skills=matching,
        missing_skills=missing,
        max_skills=max_skills,
        output_format=output_format,
        model=model,
    )

    return {
        "job_description": job_text,
        "job_skills": job_skills,
        "matching_skills": matching,
        "missing_skills": missing,
        "rewritten_cv": rewritten,
    }
