"""
MLForge Analyzer — calls Gemini API to understand ML project requirements.

Design decisions:
- Uses gemini-2.0-flash (fast + cheap, ideal for structured extraction)
- Asks Gemini to return strict JSON so we can parse it reliably
- Falls back to heuristics if API key is missing OR the call fails
- Retry once on network errors before giving up
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────────────

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

TIMEOUT_SECONDS = 15

# Valid values — used for validation after Gemini responds
VALID_PROBLEM_TYPES = {"Classification", "Regression", "Clustering"}
VALID_ALGORITHMS = {
    "XGBoost", "RandomForest", "LinearRegression",
    "LogisticRegression", "KMeans", "SVM", "NeuralNetwork",
}

# Prompt we send to Gemini — very explicit so the model returns clean JSON
ANALYSIS_PROMPT = """\
You are an ML engineering assistant. A user wants to build an ML project.

Project idea: "{prompt}"

Analyze this and return ONLY a valid JSON object — no markdown, no explanation, \
no code fences. The JSON must have exactly these keys:

{{
  "problemType": "<one of: Classification, Regression, Clustering>",
  "primaryAlgorithm": "<one of: XGBoost, RandomForest, LinearRegression, \
LogisticRegression, KMeans, SVM, NeuralNetwork>",
  "libraries": ["<4 python library names>"],
  "preprocessingSteps": ["<2-3 preprocessing step names>"],
  "targetColumn": "<likely target column name, or 'target' if unknown>",
  "explanation": "<1 sentence: why you chose this algorithm>"
}}

Choose the algorithm that best fits the problem. For fraud/churn/classification \
tasks use XGBoost or RandomForest. For price/sales/regression use XGBoost or \
LinearRegression. For grouping/segmentation use KMeans.
"""


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze(prompt: str, dataset_path: Optional[str] = None) -> dict:
    """
    Analyze a project description and return a structured analysis dict.

    Returns:
        {
            "problemType":        str,   # Classification / Regression / Clustering
            "primaryAlgorithm":   str,   # XGBoost / RandomForest / etc.
            "libraries":          list,  # ["pandas", "numpy", ...]
            "preprocessingSteps": list,  # ["StandardScaler", ...]
            "targetColumn":       str,   # likely target column name
            "explanation":        str,   # why this algorithm was chosen
            "source":             str,   # "gemini" or "heuristic"
            "processingTimeMs":   int,
        }
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("   ⚠  GEMINI_API_KEY not set — using heuristic analysis.")
        return _heuristic(prompt)

    start = time.time()
    try:
        result = _call_gemini_with_retry(prompt, api_key)
        result["source"] = "gemini"
        result["processingTimeMs"] = int((time.time() - start) * 1000)
        return result
    except Exception as exc:
        print(f"   ⚠  Gemini API error: {exc}")
        print("   ⚠  Falling back to heuristic analysis.")
        return _heuristic(prompt)


# ── Gemini API call ────────────────────────────────────────────────────────────

def _call_gemini_with_retry(prompt: str, api_key: str, retries: int = 2) -> dict:
    """Call Gemini API, retrying once on transient network errors."""
    last_exc = None
    for attempt in range(retries):
        try:
            return _call_gemini(prompt, api_key)
        except urllib.error.URLError as exc:
            last_exc = exc
            if attempt < retries - 1:
                print(f"   ⚠  Network error (attempt {attempt + 1}), retrying...")
                time.sleep(1)
        except (KeyError, json.JSONDecodeError, ValueError) as exc:
            # These are parsing errors — retrying won't help
            raise exc
    raise last_exc


def _call_gemini(prompt: str, api_key: str) -> dict:
    """Make a single Gemini API call and parse the JSON response."""
    instruction = ANALYSIS_PROMPT.format(prompt=prompt)

    body = json.dumps({
        "contents": [{"parts": [{"text": instruction}]}],
        # Ask for deterministic output — we need valid JSON, not creativity
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 512,
        },
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw_response = json.loads(response.read())

    # Navigate the Gemini response structure safely
    try:
        text = raw_response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise ValueError(f"Unexpected Gemini response structure: {raw_response}") from exc

    # Strip any accidental markdown fences the model may add despite instructions
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        text = "\n".join(lines[1:-1]).strip()

    parsed = json.loads(text)
    return _validate_and_normalize(parsed)


def _validate_and_normalize(data: dict) -> dict:
    """
    Validate Gemini's response and normalize values.
    Raises ValueError if required keys are missing.
    """
    required = {"problemType", "primaryAlgorithm", "libraries", "preprocessingSteps"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Gemini response missing keys: {missing}")

    # Normalize problemType — capitalize first letter for consistency
    problem = data["problemType"].strip().title()
    if problem not in VALID_PROBLEM_TYPES:
        # Try to salvage common variations
        lower = problem.lower()
        if "classif" in lower:
            problem = "Classification"
        elif "regress" in lower:
            problem = "Regression"
        elif "cluster" in lower:
            problem = "Clustering"
        else:
            problem = "Classification"  # safe default

    # Normalize algorithm
    algo = data["primaryAlgorithm"].strip()
    # Handle variations like "xgboost" → "XGBoost"
    algo_map = {
        "xgboost": "XGBoost",
        "randomforest": "RandomForest",
        "random forest": "RandomForest",
        "linearregression": "LinearRegression",
        "linear regression": "LinearRegression",
        "logisticregression": "LogisticRegression",
        "logistic regression": "LogisticRegression",
        "kmeans": "KMeans",
        "k-means": "KMeans",
        "svm": "SVM",
        "neuralnetwork": "NeuralNetwork",
        "neural network": "NeuralNetwork",
    }
    algo = algo_map.get(algo.lower(), algo)

    # Ensure libraries is a list of strings
    libraries = data.get("libraries", [])
    if not isinstance(libraries, list):
        libraries = ["pandas", "numpy", "scikit-learn", "xgboost"]
    libraries = [str(lib).strip() for lib in libraries][:6]  # cap at 6

    # Ensure preprocessingSteps is a list
    steps = data.get("preprocessingSteps", [])
    if not isinstance(steps, list):
        steps = ["StandardScaler", "LabelEncoder"]
    steps = [str(s).strip() for s in steps][:4]  # cap at 4

    return {
        "problemType":        problem,
        "primaryAlgorithm":   algo,
        "libraries":          libraries,
        "preprocessingSteps": steps,
        "targetColumn":       str(data.get("targetColumn", "target")).strip(),
        "explanation":        str(data.get("explanation", "")).strip(),
    }


# ── Heuristic fallback ─────────────────────────────────────────────────────────

def _heuristic(prompt: str) -> dict:
    """
    Rule-based analysis when Gemini is unavailable.
    Good enough for demos; not a replacement for real AI analysis.
    """
    lower = prompt.lower()

    # Determine problem type + algorithm from keywords
    if any(w in lower for w in ("forecast", "price", "revenue", "stock", "temperature", "predict")):
        problem, algo = "Regression", "XGBoost"
    elif any(w in lower for w in ("fraud", "churn", "spam", "disease", "diagnos", "detect", "classify", "sentiment")):
        problem, algo = "Classification", "RandomForest"
    elif any(w in lower for w in ("cluster", "segment", "group", "anomaly", "customer segment")):
        problem, algo = "Clustering", "KMeans"
    elif "weather" in lower:
        problem, algo = "Regression", "XGBoost"
    elif "recommend" in lower:
        problem, algo = "Clustering", "KMeans"
    else:
        problem, algo = "Classification", "XGBoost"

    # Pick libraries based on algorithm
    base_libs = ["pandas", "numpy", "scikit-learn"]
    if algo in ("XGBoost", "RandomForest"):
        libs = base_libs + ["xgboost"]
    elif algo == "KMeans":
        libs = base_libs + ["matplotlib"]
    else:
        libs = base_libs + ["xgboost"]

    return {
        "problemType":        problem,
        "primaryAlgorithm":   algo,
        "libraries":          libs,
        "preprocessingSteps": ["StandardScaler", "LabelEncoder"],
        "targetColumn":       "target",
        "explanation":        f"Heuristic: chose {algo} for {problem.lower()} based on prompt keywords.",
        "source":             "heuristic",
        "processingTimeMs":   5,
    }
