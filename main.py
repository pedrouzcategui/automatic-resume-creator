from utils.job_post import extract_job_details_from_job_post_url

def main():
    url = input("Enter the URL of the job posting: ")
    details = extract_job_details_from_job_post_url(url)
    print("Extracted Job Post Details:")
    for key, value in details.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()