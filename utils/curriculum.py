from pypdf import PdfReader

def extract_text_from_curriculum(cv: str):
    reader = PdfReader(cv)
    page = reader.pages[0]
    return page.extract_text()