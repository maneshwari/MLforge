"""
MLForge AI Analyzer — calls Gemini API to understand the ML project requirements.
Falls back to heuristic analysis if API key is missing or call fails.
"""

import os
import json
import time
import urllib.request
import urllib.error

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def analyze(prompt: str, dataset_path: str | None = None) -> dict:
    """Return analysis dict: problemType, primaryAlgorithm, libraries, preprocessingSteps."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("   ⚠  GEMINI_API_KEY not set — using heuristic analysis.")
        return _heuristic(prompt)

    start = time.time()
    try:
        result = _call_gemini(prompt, api_key)
        result["processingTimeMs"] = int((time.time() - start) * 1000)
        return result
    except Exception as e:
        print(f"   ⚠  Gemini API failed ({e}) — using heuristic analysis.")
        return _heuristic(prompt)


# ── Gemini API call ────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, api_key: str) -> dict:
    instruction = (
        f"Analyze this ML project idea: '{prompt}'. "
        "Return ONLY a valid JSON object (no markdown, no code fences) with exactly these keys: "
        "\"problemType\" (one of: Classification, Regression, Clustering), "
        "\"primaryAlgorithm\" (one of: XGBoost, RandomForest, LinearRegression, LogisticRegression), "
        "\"libraries\" (JSON array of 4 python library names as strings), "
        "\"preprocessingSteps\" (JSON array of 2-3 step names as strings). "
        "Example: {\"problemType\":\"Classification\",\"primaryAlgorithm\":\"XGBoost\","
        "\"libraries\":[\"pandas\",\"numpy\",\"scikit-learn\",\"xgboost\"],"
        "\"preprocessingSteps\":[\"StandardScaler\",\"LabelEncoder\"]}"
    )

    body = json.dumps({
        "contents": [{"parts": [{"text": instruction}]}]
    }).encode()

    req = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read())

    text = (
        raw["candidates"][0]["content"]["parts"][0]["text"]
        .replace("```json", "").replace("```", "").strip()
    )
    return json.loads(text)


# ── Heuristic fallback ─────────────────────────────────────────────────────────

def _heuristic(prompt: str) -> dict:
    lower = prompt.lower()

    if any(w in lower for w in ("forecast", "price", "sales", "revenue", "stock", "temperature")):
        problem, algo = "Regression", "XGBoost"
    elif any(w in lower for w in ("fraud", "churn", "spam", "disease", "diagnos", "detect", "classify")):
        problem, algo = "Classification", "RandomForest"
    elif any(w in lower for w in ("cluster", "segment", "group", "anomaly")):
        problem, algo = "Clustering", "RandomForest"
    elif "predict" in lower or "weather" in lower:
        problem, algo = "Regression", "XGBoost"
    else:
        problem, algo = "Classification", "XGBoost"

    return {
        "problemType": problem,
        "primaryAlgorithm": algo,
        "libraries": ["pandas", "numpy", "scikit-learn", "xgboost"],
        "preprocessingSteps": ["StandardScaler", "LabelEncoder"],
        "processingTimeMs": 10,
    }
