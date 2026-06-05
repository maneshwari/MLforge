"""
Quick Gemini API diagnostic — tests which model names work.
Run: python gemini_debug.py
"""
import os, json, urllib.request, urllib.error

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("ERROR: GEMINI_API_KEY not set")
    exit(1)

# Models to try in order — Gemini renames things frequently
MODELS_TO_TRY = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",  
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
]

BASE = "https://generativelanguage.googleapis.com/v1beta/models"

print(f"Testing API key: {api_key[:8]}...{api_key[-4:]}\n")

for model in MODELS_TO_TRY:
    url = f"{BASE}/{model}:generateContent?key={api_key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": "Say hello in one word."}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10},
    }).encode()

    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"  ✓ {model} → response: '{text.strip()}'")
            print(f"\n  USE THIS MODEL: {model}\n")
            break
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()[:120]
        print(f"  ✗ {model} → HTTP {e.code}: {body_err}")
    except Exception as e:
        print(f"  ✗ {model} → {e}")

