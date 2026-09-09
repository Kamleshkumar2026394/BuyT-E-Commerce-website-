import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

print("Gemini API key loaded:", bool(api_key))

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured.")

client = genai.Client(
    api_key=api_key,
    http_options={
        "timeout": 60000
    }
)


def ask_ai(prompt):
    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "Sorry, I couldn't generate a response."

    except Exception as e:

        print("====================================")
        print("GEMINI AI ERROR:", repr(e))
        print("ERROR TYPE:", type(e).__name__)
        print("====================================")

        return "Sorry, the BuyT AI assistant is temporarily unavailable."