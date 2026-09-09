import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

print("Gemini API key loaded:", bool(api_key))

client = genai.Client(
    api_key=api_key,
    http_options={
        "timeout": 20000
    }
)


def ask_ai(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        print("GEMINI AI ERROR:", repr(e))
        raise