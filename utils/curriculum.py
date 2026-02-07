'''
What I want to do, is to:
- Upload a file (my curriculum)
- Have the A.I analyze it, and segment into parts:
    - Title
    - About Me
    - Job Experience (I do not need to modify the content, but I need to modify the description of the job experience)
    - Skills (I should only keep a certain number of skills)
    - Courses (This might be in another iteration)
'''

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import os
import re


_SECTION_ALIASES = {
    "title": ["title", "name"],
    "about_me": ["about", "about me", "summary", "profile", "objective"],
    "job_experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
    ],
    "skills": ["skills", "technical skills", "core skills", "technologies"],
    "courses": ["courses", "coursework", "certifications", "training"],
}


def _load_cv_text(cv: Union[str, os.PathLike]) -> str:
    if isinstance(cv, os.PathLike) or (isinstance(cv, str) and os.path.exists(cv)):
        path = os.fspath(cv)
        if path.lower().endswith(".pdf"):
            return _read_pdf_text(path)
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    if isinstance(cv, str):
        return cv
    raise TypeError("cv must be a path or raw text")


def _read_pdf_text(path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("pypdf is required to read PDF files") from exc

    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def _normalize_lines(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    return lines


def _is_heading(line: str) -> Optional[str]:
    if not line:
        return None
    normalized = re.sub(r"[^a-z0-9\s]", "", line.lower()).strip()
    for key, aliases in _SECTION_ALIASES.items():
        if normalized in aliases:
            return key
    if len(normalized) > 0 and len(normalized) <= 30:
        for key, aliases in _SECTION_ALIASES.items():
            for alias in aliases:
                if normalized == alias:
                    return key
    return None


def _segment_by_headings(lines: List[str]) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current_key: Optional[str] = None
    for line in lines:
        heading = _is_heading(line)
        if heading:
            current_key = heading
            sections.setdefault(current_key, [])
            continue
        if current_key:
            sections[current_key].append(line)
    return sections


def _first_non_empty(lines: List[str]) -> str:
    for line in lines:
        if line:
            return line
    return ""


def _extract_about_me(lines: List[str], sections: Dict[str, List[str]]) -> str:
    about_lines = sections.get("about_me")
    if about_lines:
        return "\n".join([line for line in about_lines if line])

    # Fallback: take the first paragraph after the title
    non_empty = [line for line in lines if line]
    if len(non_empty) <= 1:
        return ""
    return non_empty[1]


def _split_list_items(text_block: str) -> List[str]:
    if not text_block:
        return []
    raw_items = re.split(r"[\n,;\-]+", text_block)
    items = [item.strip() for item in raw_items if item.strip()]
    return items


def _looks_like_entry_start(line: str) -> bool:
    if not line:
        return False
    date_pattern = r"(\b(19|20)\d{2}\b|\b\w{3,9}\s+\d{4}\b|\b\d{1,2}/\d{4}\b)"
    if re.search(date_pattern, line):
        return True
    if " - " in line or " | " in line:
        return True
    return False


def _parse_job_experience(lines: List[str]) -> List[Dict[str, Union[str, List[str]]]]:
    entries: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if not line:
            if current:
                entries.append(current)
                current = []
            continue
        if _looks_like_entry_start(line) and current:
            entries.append(current)
            current = [line]
            continue
        current.append(line)
    if current:
        entries.append(current)

    parsed: List[Dict[str, Union[str, List[str]]]] = []
    for entry in entries:
        header = entry[0] if entry else ""
        details = entry[1:] if len(entry) > 1 else []
        parsed.append(
            {
                "header": header,
                "details": details,
                "description": details,
                "raw": "\n".join(entry),
            }
        )
    return parsed


def extract_job_details_from_cv(cv: Union[str, os.PathLike]) -> Dict[str, object]:
    text = _load_cv_text(cv)
    lines = _normalize_lines(text)

    title = _first_non_empty(lines)
    sections = _segment_by_headings(lines)

    about_me = _extract_about_me(lines, sections)

    skills_text = "\n".join([line for line in sections.get("skills", []) if line])
    skills = _split_list_items(skills_text)

    courses_text = "\n".join([line for line in sections.get("courses", []) if line])
    courses = _split_list_items(courses_text)

    job_experience_lines = [line for line in sections.get("job_experience", [])]
    job_experience = _parse_job_experience(job_experience_lines)

    return {
        "title": title,
        "about_me": about_me,
        "job_experience": job_experience,
        "skills": skills,
        "courses": courses,
        "raw_sections": sections,
    }