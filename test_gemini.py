import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found")
    exit(1)

print(f"Testing API Key: {api_key[:5]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    resp = httpx.get(url, timeout=10.0)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        models = resp.json().get('models', [])
        with open("models.txt", "w", encoding="utf-8") as f:
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    f.write(m['name'] + "\n")
        print("Models written to models.txt")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")
