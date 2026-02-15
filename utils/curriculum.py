from pypdf import PdfReader

def extract_text_from_curriculum(cv: str):
    reader = PdfReader(cv)
    page = reader.pages[0]
    return page.extract_text()

def extract_skills_from_curriculum_text(cv_text: str, skills: set[str]):
    cv_text_lower = cv_text.lower()
    skills_in_cv = {skill for skill in skills if skill.lower() in cv_text_lower}
    skills_missing = skills - skills_in_cv
    return {
        "skills_match": skills_in_cv,
        "skills_missing": skills_missing
    }