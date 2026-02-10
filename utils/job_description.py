import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import markdownify

job_description_url = "https://weworkremotely.com/remote-jobs/bluelight-consulting-devops-engineer-remote-latin-america"

def extract_text_from_job_description(job_description_url: str):
    # Use Playwright to render the page (headless) with a browser-like User-Agent.
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    )

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent, locale="en-US")
            page = context.new_page()
            try:
                page.goto(job_description_url, wait_until="networkidle", timeout=20000)
            except PlaywrightTimeoutError:
                # try a shorter wait if networkidle times out
                page.goto(job_description_url, timeout=15000)

            # Prefer the specific job description element so we only extract that text
            handle = page.query_selector(".lis-container__job__content__description")
            if handle:
                html = handle.inner_html()
            else:
                html = page.content()
            browser.close()

    except Exception as e:
        print("Playwright request failed:", e)
        raise

    # Convert rendered HTML to Markdown
    markdown_content = markdownify.markdownify(html, heading_style="ATX")
    print(markdown_content)
    return markdown_content


def find_skills_gap(job_skills: set, candidate_skills: set):
    job_set = {s.lower() for s in job_skills}
    candidate_set = {s.lower() for s in candidate_skills}

    matching_skills = job_set.intersection(candidate_set)

    missing_skills = job_set - candidate_set

    return list(matching_skills), list(missing_skills)

extract_text_from_job_description(job_description_url)