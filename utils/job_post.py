from typing import Any
from urllib.parse import urlparse

from api.chatgpt import ChatGPTService
from data.skills import skills as global_skills_list


def extract_job_details_from_job_post_url(url: str, model: str = "gpt-5-mini") -> dict[str, Any]:
    parsed_url = urlparse(url)
    domain = (parsed_url.netloc or "").lower()
    if domain.startswith("www."):
        domain = domain[4:]

    canonical_skills = sorted(global_skills_list)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "company_name": {"type": ["string", "null"]},
            "job_title": {"type": ["string", "null"]},
            "job_description": {"type": ["string", "null"]},
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "optional_skills": {"type": "array", "items": {"type": "string"}},
            "salary_range": {"type": ["string", "null"]},
        },
        "required": [
            "company_name",
            "job_title",
            "job_description",
            "required_skills",
            "optional_skills",
            "salary_range",
        ],
        "additionalProperties": False,
    }

    instructions = (
        "You are a job-posting extraction agent. You have access to the web_search tool. "
        "Use web_search to locate and open the job posting page, then find the relevant fields. "
        "Prefer authoritative sources and the job posting page itself. "
        "If a field cannot be found, return null (or an empty array). "
        "Only include hard skills (technologies, tools, certifications)."
    )

    prompt = (
        "Extract the following fields from this job posting URL:\n"
        "1) Company Name\n"
        "2) Job Title\n"
        "3) Job Description\n"
        "4) Required Skills\n"
        "5) Optional Skills\n"
        "6) Salary Range (if found)\n\n"
        f"Job posting URL: {url}\n\n"
        "Normalize skill names where possible using this canonical list (but you may include extras if present):\n"
        f"{canonical_skills}"
    )

    tools: list[dict[str, Any]] = [{"type": "web_search"}]
    if domain:
        tools = [
            {
                "type": "web_search",
                "filters": {"allowed_domains": [domain]},
            }
        ]

    extracted = ChatGPTService.generate_json(
        prompt=prompt,
        model=model,
        instructions=instructions,
        schema=schema,
        schema_name="job_post_details",
        tools=tools,
        tool_choice="auto",
        reasoning={"effort": "low"},
        include=["web_search_call.action.sources"],
    )

    def as_str_or_none(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned if cleaned else None
        return str(value).strip() or None

    def as_string_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        out: list[str] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                continue
            cleaned = item.strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(cleaned)
        return out

    return {
        "company_name": as_str_or_none(extracted.get("company_name")),
        "job_title": as_str_or_none(extracted.get("job_title")),
        "job_description": as_str_or_none(extracted.get("job_description")),
        "required_skills": as_string_list(extracted.get("required_skills")),
        "optional_skills": as_string_list(extracted.get("optional_skills")),
        "salary_range": as_str_or_none(extracted.get("salary_range")),
    }