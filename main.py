from __future__ import annotations

from utils.job_pipeline import tailor_resume_from_url


def main():
    job_url = input("Paste the job URL: ").strip()
    if not job_url:
        raise ValueError("Job URL is required")

    result = tailor_resume_from_url(job_url=job_url, cv="cv.pdf", max_skills=12)

    print("\n=== Rewritten CV ===\n")
    print(result["rewritten_cv"])

if __name__ == "__main__":
    main()
