"""
MLForge Project Generator
Writes a complete, runnable ML project to disk given a prompt + analysis result.
"""

import os
import re
import subprocess
from pathlib import Path


# ── Public API ─────────────────────────────────────────────────────────────────

def generate(output_dir: str, prompt: str, analysis: dict, mode: str = "standard") -> str:
    project_name = _sanitize(prompt)
    root = Path(output_dir) / project_name
    root.mkdir(parents=True, exist_ok=True)

    scope = {
        "project_name":        project_name.replace("_", " ").title(),
        "project_prompt":      prompt,
        "problem_type":        analysis["problemType"],
        "primary_algorithm":   analysis["primaryAlgorithm"],
        "libraries":           ", ".join(analysis["libraries"]),
        "preprocessing_steps": ", ".join(analysis["preprocessingSteps"]),
    }
    is_regression = analysis["problemType"].lower() == "regression"

    _mk(root, [
        "data/raw", "data/processed",
        "src/ml_pipeline", "src/backend", "src/frontend",
        "tests", ".github/workflows",
    ])

    _write(root / "src/ml_pipeline/__init__.py", "")
    _write(root / "src/ml_pipeline/preprocessing.py", _preprocessing())
    _write(root / "src/ml_pipeline/training.py",      _training(is_regression))
    _write(root / "src/ml_pipeline/evaluation.py",    _evaluation())
    _write(root / "src/backend/main.py",              _backend(scope))
    _write(root / "src/frontend/app.py",              _frontend(scope))
    _write(root / "Dockerfile",                       _dockerfile())
    _write(root / "docker-compose.yml",               _compose())
    _write(root / "requirements.txt",                 _requirements())
    _write(root / "README.md",                        _readme(scope))
    _write(root / ".gitignore",                       _gitignore())
    _write(root / "data/raw/sample_data.csv",         _sample_csv(is_regression))

    _git_init(root)
    return str(root)


# ── File contents ──────────────────────────────────────────────────────────────

def _preprocessing():
    return '''\
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.fillna(df.mean(numeric_only=True))
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
        if num_cols:
            df[num_cols] = self.scaler.fit_transform(df[num_cols])
        for col in cat_cols:
            enc = LabelEncoder()
            df[col] = enc.fit_transform(df[col].astype(str))
            self.encoders[col] = enc
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.fillna(df.mean(numeric_only=True))
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            df[num_cols] = self.scaler.transform(df[num_cols])
        return df
'''


def _training(is_regression: bool):
    model_cls   = "XGBRegressor"    if is_regression else "XGBClassifier"
    metric_fn   = "mean_squared_error" if is_regression else "accuracy_score"
    metric_name = "MSE"             if is_regression else "Accuracy"
    metric_fmt  = ".4f"

    return f'''\
import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import {metric_fn}
from xgboost import {model_cls}
from preprocessing import DataPreprocessor


class ModelTrainer:
    def __init__(self):
        self.model = {model_cls}(n_estimators=100, max_depth=5, random_state=42)
        self.preprocessor = DataPreprocessor()

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        X_proc = self.preprocessor.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_proc, y, test_size=test_size, random_state=42
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        score = {metric_fn}(y_test, y_pred)
        print(f"  {metric_name}: {{score:{metric_fmt}}}")
        return score

    def save(self, path: str = "model.joblib"):
        joblib.dump(self.model, path)
        joblib.dump(self.preprocessor, "preprocessor.joblib")
        print(f"  Model saved → {{path}}")

    def predict(self, X: pd.DataFrame):
        X_proc = self.preprocessor.transform(X)
        return self.model.predict(X_proc)


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "../../data/raw/sample_data.csv")

    if not os.path.exists(data_path):
        print("Sample data not found — generating synthetic data...")
        rng = np.random.default_rng(42)
        n = 200
        df = pd.DataFrame({{
            "feature1": rng.normal(50, 10, n),
            "feature2": rng.normal(20, 5,  n),
            "feature3": rng.uniform(0, 100, n),
            "feature4": rng.normal(5, 2,   n),
            "target":   rng.integers(0, 2, n) if not {str(is_regression).lower() == "true"!r} else rng.normal(100, 20, n),
        }})
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_csv(data_path, index=False)
        print("  Synthetic data created.")

    data = pd.read_csv(data_path)
    X = data.drop("target", axis=1)
    y = data["target"]

    print("Training model...")
    trainer = ModelTrainer()
    trainer.train(X, y)
    trainer.save()
    print("Done! ✓")
'''


def _evaluation():
    return '''\
import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix, mean_squared_error
)


class ModelEvaluator:
    def __init__(self, model_path="model.joblib", prep_path="preprocessor.joblib"):
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(prep_path)

    def evaluate(self, X: pd.DataFrame, y):
        X_proc = self.preprocessor.transform(X)
        y_pred = self.model.predict(X_proc)
        try:
            print(classification_report(y, y_pred))
            print("Confusion Matrix:")
            print(confusion_matrix(y, y_pred))
        except Exception:
            mse = mean_squared_error(y, y_pred)
            print(f"MSE: {mse:.4f}  |  RMSE: {mse**0.5:.4f}")
'''


def _backend(scope: dict):
    return f'''\
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../ml_pipeline"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(
    title="{scope["project_name"]} API",
    description="{scope["project_prompt"]}",
    version="1.0.0",
)

_base = os.path.dirname(__file__)
_model_path = os.path.join(_base, "../ml_pipeline/model.joblib")
_prep_path  = os.path.join(_base, "../ml_pipeline/preprocessor.joblib")

try:
    _model = joblib.load(_model_path)
    _prep  = joblib.load(_prep_path)
    MODEL_LOADED = True
except Exception as e:
    _model = _prep = None
    MODEL_LOADED = False
    print(f"[warn] Model not loaded: {{e}}")


class PredictionInput(BaseModel):
    features: dict


class PredictionOutput(BaseModel):
    prediction: float
    status: str = "success"


@app.get("/health")
async def health():
    return {{"status": "healthy", "model_loaded": MODEL_LOADED}}


@app.post("/predict", response_model=PredictionOutput)
async def predict(body: PredictionInput):
    if not MODEL_LOADED:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Run: cd src/ml_pipeline && python training.py",
        )
    try:
        df   = pd.DataFrame([body.features])
        X    = _prep.transform(df)
        pred = _model.predict(X)[0]
        return PredictionOutput(prediction=float(pred))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


def _frontend(scope: dict):
    return f'''\
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="{scope["project_name"]}", layout="wide")
st.title("🤖 {scope["project_name"]}")
st.caption(
    f"**{scope["project_prompt"]}** | "
    "Algorithm: **{scope["primary_algorithm"]}** | "
    "Type: **{scope["problem_type"]}**"
)

API = "http://localhost:8000"
page = st.sidebar.radio("Navigation", ["🔮 Predict", "📊 Batch", "ℹ️ About"])

if page == "🔮 Predict":
    st.header("Single Prediction")
    with st.form("f"):
        c1, c2 = st.columns(2)
        f1 = c1.number_input("Feature 1", value=1.0)
        f2 = c1.number_input("Feature 2", value=2.0)
        f3 = c2.number_input("Feature 3", value=3.0)
        f4 = c2.number_input("Feature 4", value=4.0)
        go = st.form_submit_button("🔮 Predict")
    if go:
        try:
            r = requests.post(f"{{API}}/predict",
                              json={{"features": {{"feature1": f1, "feature2": f2,
                                                  "feature3": f3, "feature4": f4}}}},
                              timeout=5)
            d = r.json()
            if r.status_code == 200:
                st.success(f"Prediction: **{{d[\'prediction\']:.4f}}**")
            else:
                st.error(d.get("detail", "Unknown error"))
        except Exception as e:
            st.warning(f"API unreachable: {{e}}\\n\\nRun: `python src/backend/main.py`")

elif page == "📊 Batch":
    st.header("Batch Prediction")
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f:
        df = pd.read_csv(f)
        st.dataframe(df.head())
        st.info("Wire batch prediction in src/backend/main.py")

else:
    st.header("About")
    st.markdown(f"""
| Field | Value |
|---|---|
| Problem | {scope["project_prompt"]} |
| Type | {scope["problem_type"]} |
| Algorithm | {scope["primary_algorithm"]} |
| Libraries | {scope["libraries"]} |
| Preprocessing | {scope["preprocessing_steps"]} |
""")
    st.markdown("---")
    st.caption("Generated with **MLForge** 🚀 — ML SMITHS, OIST Bhopal")
'''


def _dockerfile():
    return '''\
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["python", "src/backend/main.py"]
'''


def _compose():
    return '''\
version: "3.8"
services:
  backend:
    build: .
    ports: ["8000:8000"]
    environment: [PYTHONUNBUFFERED=1]
  frontend:
    build: .
    ports: ["8501:8501"]
    command: streamlit run src/frontend/app.py --server.address=0.0.0.0
    depends_on: [backend]
'''


def _requirements():
    return '''\
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
xgboost>=2.0
fastapi>=0.109
uvicorn>=0.27
streamlit>=1.31
joblib>=1.3
pydantic>=2.0
requests>=2.31
'''


def _readme(scope: dict):
    return f'''\
# {scope["project_name"]}

> {scope["project_prompt"]}

Generated with **MLForge** — AI-powered ML scaffolding | ML SMITHS, OIST Bhopal

## Quick Start

```bash
pip install -r requirements.txt
cd src/ml_pipeline && python training.py
cd ../.. && python src/backend/main.py       # http://localhost:8000/docs
streamlit run src/frontend/app.py            # http://localhost:8501
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/predict` | POST | Single prediction |
| `/docs` | GET | Swagger UI |

### Example

```bash
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d \'{{"features": {{"feature1": 1.0, "feature2": 2.0, "feature3": 3.0, "feature4": 4.0}}}}\' 
```

## Project Info

| Field | Value |
|---|---|
| Problem Type | {scope["problem_type"]} |
| Algorithm | {scope["primary_algorithm"]} |
| Libraries | {scope["libraries"]} |
| Preprocessing | {scope["preprocessing_steps"]} |

## Structure

```
.
├── data/raw/            # Raw input data (sample_data.csv included)
├── src/
│   ├── ml_pipeline/     # preprocessing.py · training.py · evaluation.py
│   ├── backend/         # FastAPI — main.py
│   └── frontend/        # Streamlit — app.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
'''


def _gitignore():
    return '''\
__pycache__/
*.pyc
*.pyo
*.joblib
.env
.DS_Store
venv/
.venv/
'''


def _sample_csv(is_regression: bool, n: int = 100) -> str:
    import random
    rng = random.Random(42)
    rows = ["feature1,feature2,feature3,feature4,target"]
    for _ in range(n):
        f1 = round(rng.gauss(50, 10), 2)
        f2 = round(rng.gauss(20, 5),  2)
        f3 = round(rng.uniform(0, 100), 2)
        f4 = round(rng.gauss(5, 2),   2)
        target = round(f1 * 0.3 + f2 * 0.5 + rng.gauss(0, 2), 2) if is_regression \
                 else rng.randint(0, 1)
        rows.append(f"{f1},{f2},{f3},{f4},{target}")
    return "\n".join(rows) + "\n"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _mk(root: Path, dirs: list[str]):
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)


def _write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def _git_init(root: Path):
    try:
        subprocess.run(["git", "init"], cwd=root, capture_output=True)
    except Exception:
        pass


def _sanitize(prompt: str) -> str:
    name = re.sub(r"[^a-z0-9 ]", " ", prompt.lower())
    name = re.sub(r"\s+", "_", name.strip())
    return name.strip("_") or "ml_project"
