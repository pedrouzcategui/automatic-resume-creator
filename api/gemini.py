import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", 
    config=types.GenerateContentConfig(
        system_instruction=""
    ),
    contents="Explain how AI works in a few words"
)

# Maybe I can just return an object of 4 keys instead
def change_job_experience_description():
    pass

def change_skills_based_on_job_description():
    pass

def change_certifications_based_on_job_description():
    pass

def change_about_me_based_on_job_description():
    pass

print(response.text)