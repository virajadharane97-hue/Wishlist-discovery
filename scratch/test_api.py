import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY_2")
print("Key loaded:", api_key[:15] + "..." if api_key else "None")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Return a JSON object: {\"status\": \"success\"}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.0
    )
)
print("Response text:", response.text)
