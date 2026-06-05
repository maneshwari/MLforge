"""
MLForge Project Generator.

Writes a complete, runnable ML project to disk given a prompt + analysis result.

Design decisions:
- All template strings live here (no external files needed to run)
- Templates use simple .format() — readable and debuggable
- Each _write_* function is responsible for one file
- The public generate() function orchestrates everything
"""

import os
import re
import random
import subprocess
from pathlib import Path
from typing import Optional


# ── Public API ─────────────────────────────────────────────────────────────────

def generate(
    output_dir: str,
    prompt: str,
    analysis: dict,
    mode: str = "standard",
    template: str = "base",
) -> str:
    """
    Generate a complete ML project directory.

    Args:
        output_dir:  Where to create the project folder.
        prompt:      The original user description.
        analysis:    Dict from analyzer.analyze().
        mode:        "standard" or "hackathon".
        template:    "base", "healthcare", "fintech", or "agritech".

    Returns:
        Absolute path to the generated project directory.
    """
    project_name = _sanitize_name(prompt)
    root = Path(output_dir).resolve() / project_name
    root.mkdir(parents=True, exist_ok=True)

    # Build the scope dict — everything templates need
    scope = _build_scope(project_name, prompt, analysis, template)
    is_regression = analysis["problemType"].lower() == "regression"
    is_clustering = analysis["problemType"].lower() == "clustering"

    # Create directory structure
    _make_dirs(root, [
        "data/raw",
        "data/processed",
        "src/ml_pipeline",
        "src/backend",
        "src/frontend",
        "tests",
        ".github/workflows",
    ])

    # Write all project files
    _write(root / "src/ml_pipeline/__init__.py", "")
    _write(root / "src/ml_pipeline/preprocessing.py", _preprocessing_py())
    _write(root / "src/ml_pipeline/training.py",      _training_py(scope, is_regression, is_clustering))
    _write(root / "src/ml_pipeline/evaluation.py",    _evaluation_py(is_regression, is_clustering))
    _write(root / "src/backend/__init__.py",          "")
    _write(root / "src/backend/main.py",              _backend_py(scope))
    _write(root / "src/frontend/__init__.py",         "")
    _write(root / "src/frontend/app.py",              _frontend_py(scope))
    _write(root / "data/raw/sample_data.csv",         _sample_csv(is_regression, is_clustering))
    _write(root / "Dockerfile",                       _dockerfile())
    _write(root / "docker-compose.yml",               _compose())
    _write(root / "requirements.txt",                 _requirements(analysis))
    _write(root / ".gitignore",                       _gitignore())
    _write(root / ".env.example",                     _env_example())
    _write(root / ".github/workflows/ci.yml",         _ci_yml())
    _write(root / "README.md",                        _readme(scope))

    # Standard mode extras
    if mode == "standard":
        _write(root / "ARCHITECTURE.md", _architecture_md(scope))
        _write(root / "tests/test_preprocessing.py", _test_preprocessing())
        _write(root / "tests/test_model.py",          _test_model(scope))
        _write(root / "tests/test_api.py",            _test_api(scope))
        _write(root / "health.json",                  _health_json(scope))

    _git_init(root)
    return str(root)


# ── Scope builder ──────────────────────────────────────────────────────────────

def _build_scope(project_name: str, prompt: str, analysis: dict, template: str) -> dict:
    """Build the template scope dict from analysis results."""
    algo = analysis["primaryAlgorithm"]

    # Map algorithm to its import and class name
    algo_imports = {
        "XGBoost":           ("xgboost", "XGBClassifier", "XGBRegressor"),
        "RandomForest":      ("sklearn.ensemble", "RandomForestClassifier", "RandomForestRegressor"),
        "LinearRegression":  ("sklearn.linear_model", "LogisticRegression", "LinearRegression"),
        "LogisticRegression":("sklearn.linear_model", "LogisticRegression", "LogisticRegression"),
        "KMeans":            ("sklearn.cluster", "KMeans", "KMeans"),
        "SVM":               ("sklearn.svm", "SVC", "SVR"),
        "NeuralNetwork":     ("sklearn.neural_network", "MLPClassifier", "MLPRegressor"),
    }

    problem = analysis["problemType"]
    is_regression = problem.lower() == "regression"
    module, clf_class, reg_class = algo_imports.get(algo, ("xgboost", "XGBClassifier", "XGBRegressor"))
    model_class = reg_class if is_regression else clf_class

    return {
        "project_name":        project_name.replace("_", " ").title(),
        "project_slug":        project_name,
        "project_prompt":      prompt,
        "problem_type":        problem,
        "primary_algorithm":   algo,
        "model_module":        module,
        "model_class":         model_class,
        "libraries":           analysis["libraries"],
        "libraries_str":       ", ".join(analysis["libraries"]),
        "preprocessing_steps": analysis["preprocessingSteps"],
        "preprocessing_str":   ", ".join(analysis["preprocessingSteps"]),
        "target_column":       analysis.get("targetColumn", "target"),
        "explanation":         analysis.get("explanation", ""),
        "template":            template,
        "source":              analysis.get("source", "heuristic"),
    }


# ── File content generators ────────────────────────────────────────────────────

def _preprocessing_py() -> str:
    return '''\
"""
Data preprocessing pipeline.

Why StandardScaler?
  Neural nets and distance-based models (SVM, KMeans) are sensitive to scale.
  Tree-based models (XGBoost, RF) are NOT, but scaling never hurts them either.
  Applying it universally keeps the pipeline consistent.

Why LabelEncoder for categoricals?
  Simple and effective for low-cardinality categoricals. For high-cardinality
  or ordinal features, consider OrdinalEncoder or TargetEncoder instead.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


class DataPreprocessor:
    """
    Fit-transform pipeline: handles missing values, scaling, encoding.
    Stores fitted transformers so the same transformations apply at inference.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: dict = {}  # one encoder per categorical column
        self.numeric_cols: list = []
        self.categorical_cols: list = []
        self._fitted = False

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit on training data and transform. Call ONCE during training."""
        df = self._fill_missing(df)

        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if self.numeric_cols:
            df[self.numeric_cols] = self.scaler.fit_transform(df[self.numeric_cols])

        for col in self.categorical_cols:
            enc = LabelEncoder()
            df[col] = enc.fit_transform(df[col].astype(str))
            self.label_encoders[col] = enc

        self._fitted = True
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using already-fitted transformers."""
        if not self._fitted:
            raise RuntimeError("Preprocessor is not fitted. Call fit_transform() first.")

        df = self._fill_missing(df)

        if self.numeric_cols:
            # Only scale columns that exist in this dataframe
            cols = [c for c in self.numeric_cols if c in df.columns]
            if cols:
                df[cols] = self.scaler.transform(df[cols])

        for col, enc in self.label_encoders.items():
            if col in df.columns:
                # Handle unseen categories gracefully
                known = set(enc.classes_)
                df[col] = df[col].astype(str).apply(
                    lambda x: x if x in known else enc.classes_[0]
                )
                df[col] = enc.transform(df[col])

        return df

    @staticmethod
    def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values:
        - Numeric: median (robust to outliers, unlike mean)
        - Categorical: most frequent value (mode)
        """
        df = df.copy()
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        for col in df.select_dtypes(include=["object", "category"]).columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].mode()[0], inplace=True)
        return df
'''


def _training_py(scope: dict, is_regression: bool, is_clustering: bool) -> str:
    """Generate training.py — tuned per problem type."""
    problem = scope["problem_type"]
    algo = scope["primary_algorithm"]
    module = scope["model_module"]
    model_class = scope["model_class"]

    # 8 spaces = method body indent level (class → def → body)
    I = "        "

    if is_clustering:
        metric_import = "from sklearn.metrics import silhouette_score"
        train_body = (
            f"{I}X_proc = self.preprocessor.fit_transform(X)\n"
            f"{I}labels = self.model.fit_predict(X_proc)\n"
            f"{I}score = silhouette_score(X_proc, labels)\n"
            f'{I}print(f"  Silhouette Score: {{score:.4f}}")\n'
            f"{I}return score"
        )
    elif is_regression:
        metric_import = "from sklearn.metrics import mean_squared_error, r2_score"
        train_body = (
            f"{I}X_proc = self.preprocessor.fit_transform(X)\n"
            f"{I}X_train, X_test, y_train, y_test = train_test_split(\n"
            f"{I}    X_proc, y, test_size=test_size, random_state=42\n"
            f"{I})\n"
            f"{I}self.model.fit(X_train, y_train)\n"
            f"{I}y_pred = self.model.predict(X_test)\n"
            f"{I}score = mean_squared_error(y_test, y_pred, squared=False)\n"
            f"{I}r2 = r2_score(y_test, y_pred)\n"
            f'{I}print(f"  RMSE: {{score:.4f}}  |  R\\u00b2: {{r2:.4f}}")\n'
            f"{I}return score"
        )
    else:
        metric_import = "from sklearn.metrics import accuracy_score, classification_report"
        train_body = (
            f"{I}X_proc = self.preprocessor.fit_transform(X)\n"
            f"{I}X_train, X_test, y_train, y_test = train_test_split(\n"
            f"{I}    X_proc, y, test_size=test_size, random_state=42\n"
            f"{I})\n"
            f"{I}self.model.fit(X_train, y_train)\n"
            f"{I}y_pred = self.model.predict(X_test)\n"
            f"{I}score = accuracy_score(y_test, y_pred)\n"
            f'{I}print(f"  Accuracy: {{score:.4f}}")\n'
            f"{I}print(classification_report(y_test, y_pred))\n"
            f"{I}return score"
        )
    save_note = ""

    # XGBoost needs a slightly different import path
    if algo == "XGBoost":
        model_import = f"from xgboost import {model_class}"
    else:
        model_import = f"from {module} import {model_class}"

    # KMeans doesn't use n_estimators / max_depth
    if is_clustering:
        model_init = f"{model_class}(n_clusters=5, random_state=42)"
    elif algo in ("LinearRegression", "LogisticRegression"):
        model_init = f"{model_class}(max_iter=1000)"
    else:
        model_init = f"{model_class}(n_estimators=100, max_depth=5, random_state=42)"

    split_import = "" if is_clustering else "from sklearn.model_selection import train_test_split"

    # Prefix each line of train_body with 8 spaces (method body indent)
    # train_body lines are already at 8 spaces; we just need to make sure
    # the template doesn't add extra indentation via the f-string alignment.
    train_body_indented = train_body  # already has 8-space indent per line

    header = f'''\
"""
Model training script for {scope["project_name"]}.

Problem type: {problem}
Algorithm:    {algo}
Why {algo}?  {scope["explanation"]}
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
{split_import}
{metric_import}
{model_import}

# Add ml_pipeline to path so preprocessing.py is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import DataPreprocessor


class ModelTrainer:
    def __init__(self):
        self.model = {model_init}
        self.preprocessor = DataPreprocessor()

    def train(self, X: pd.DataFrame, y: pd.Series = None, test_size: float = 0.2) -> float:
        """Train the model and return evaluation score."""
'''
    is_cluster_str = "True" if is_clustering else "False"
    is_cluster_str2 = is_cluster_str

    return header + train_body_indented + f'''

    def save(self, model_path: str = "model.joblib", prep_path: str = "preprocessor.joblib"):
        """Save model and preprocessor to disk for serving."""
        joblib.dump(self.model, model_path)
        joblib.dump(self.preprocessor, prep_path)
        print(f"  Model saved → {{model_path}}")
        print(f"  Preprocessor saved → {{prep_path}}")

    def predict(self, X: pd.DataFrame):
        """Run inference. Preprocessor must already be fitted (i.e., after train())."""
        X_proc = self.preprocessor.transform(X)
        return self.model.predict(X_proc)


if __name__ == "__main__":
    # ── Locate sample data ──────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "../../data/raw/sample_data.csv")

    if not os.path.exists(data_path):
        print("Sample data not found. Please add a CSV to data/raw/")
        sys.exit(1)

    print(f"Loading data from: {{data_path}}")
    data = pd.read_csv(data_path)
    print(f"  Shape: {{data.shape}}")

    # ── Split features / target ─────────────────────────────────────────────
    target_col = "{scope["target_column"]}"
    if target_col not in data.columns:
        target_col = data.columns[-1]  # fall back to last column
        print(f"  Target column not found, using: {{target_col}}")

    X = data.drop(columns=[target_col])
    y = data[target_col] if not {is_cluster_str} else None

    # ── Train ───────────────────────────────────────────────────────────────
    print("\\nTraining model...")
    trainer = ModelTrainer()

    # Save model alongside this script so the backend can find it
    model_out = os.path.join(script_dir, "model.joblib")
    prep_out   = os.path.join(script_dir, "preprocessor.joblib")

    if {is_cluster_str2}:
        trainer.train(X)
    else:
        trainer.train(X, y)

    trainer.save(model_out, prep_out)
    print("\\nDone! ✓  Run the backend: python src/backend/main.py")
'''


def _evaluation_py(is_regression: bool, is_clustering: bool) -> str:
    return '''\
"""
Model evaluation utilities.
Run this after training to get a detailed performance report.
"""

import sys
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_squared_error,
    r2_score,
    silhouette_score,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ModelEvaluator:
    def __init__(
        self,
        model_path: str = "model.joblib",
        prep_path: str = "preprocessor.joblib",
    ):
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(prep_path)

    def evaluate(self, X: pd.DataFrame, y=None) -> dict:
        """
        Evaluate the model and print a report.
        For clustering, y is ignored.
        """
        X_proc = self.preprocessor.transform(X)

        try:
            # Clustering
            labels = self.model.predict(X_proc)
            score = silhouette_score(X_proc, labels)
            print(f"Silhouette Score: {score:.4f}")
            return {"silhouette": score}
        except Exception:
            pass

        y_pred = self.model.predict(X_proc)

        try:
            # Try classification metrics first
            print("Classification Report:")
            print(classification_report(y, y_pred))
            print("Confusion Matrix:")
            print(confusion_matrix(y, y_pred))
            return {"report": classification_report(y, y_pred, output_dict=True)}
        except Exception:
            # Fall back to regression
            rmse = mean_squared_error(y, y_pred, squared=False)
            r2 = r2_score(y, y_pred)
            print(f"RMSE: {rmse:.4f}  |  R²: {r2:.4f}")
            return {"rmse": rmse, "r2": r2}
'''


def _backend_py(scope: dict) -> str:
    return f'''\
"""
FastAPI backend for {scope["project_name"]}.

Endpoints:
  GET  /health   — liveness check
  POST /predict  — single prediction
  POST /batch    — batch prediction from JSON list

Why FastAPI?
  Auto-generates OpenAPI docs at /docs (try it!).
  Async-ready, type-safe via Pydantic, and extremely fast.
"""

import os
import sys
import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import uvicorn

# ── Path setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR   = os.path.join(BASE_DIR, "../ml_pipeline")
sys.path.insert(0, ML_DIR)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="{scope["project_name"]} API",
    description="{scope["project_prompt"]}",
    version="1.0.0",
)

# Allow requests from the Streamlit frontend (localhost:8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Model loading ─────────────────────────────────────────────────────────────
_model_path = os.path.join(ML_DIR, "model.joblib")
_prep_path  = os.path.join(ML_DIR, "preprocessor.joblib")

try:
    _model = joblib.load(_model_path)
    _prep  = joblib.load(_prep_path)
    MODEL_LOADED = True
    logger.info("Model loaded successfully.")
except FileNotFoundError:
    _model = _prep = None
    MODEL_LOADED = False
    logger.warning(
        "Model files not found. Run: "
        "cd src/ml_pipeline && python training.py"
    )
except Exception as exc:
    _model = _prep = None
    MODEL_LOADED = False
    logger.error(f"Failed to load model: {{exc}}")


# ── Request / Response schemas ───────────────────────────────────────────────

class PredictionInput(BaseModel):
    features: dict[str, Any] = Field(
        ...,
        description="Feature name → value mapping",
        json_schema_extra={{"example": {{"feature1": 1.0, "feature2": 2.0, "feature3": 3.0, "feature4": 4.0}}}},
    )


class PredictionOutput(BaseModel):
    prediction: Any
    status: str = "success"
    model_algorithm: str = "{scope["primary_algorithm"]}"


class BatchInput(BaseModel):
    records: list[dict[str, Any]] = Field(
        ...,
        description="List of feature dicts",
    )


class BatchOutput(BaseModel):
    predictions: list[Any]
    count: int
    status: str = "success"


class HealthOutput(BaseModel):
    status: str
    model_loaded: bool
    algorithm: str
    problem_type: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthOutput, tags=["System"])
async def health():
    """Liveness check — also tells the frontend if the model is ready."""
    return HealthOutput(
        status="healthy" if MODEL_LOADED else "model_not_loaded",
        model_loaded=MODEL_LOADED,
        algorithm="{scope["primary_algorithm"]}",
        problem_type="{scope["problem_type"]}",
    )


@app.post("/predict", response_model=PredictionOutput, tags=["Inference"])
async def predict(body: PredictionInput):
    """
    Single prediction endpoint.

    Send a JSON body with a \\"features\\" key containing a dict of feature
    names to values. Returns the model's prediction.
    """
    _require_model()
    try:
        df   = pd.DataFrame([body.features])
        X    = _prep.transform(df)
        pred = _model.predict(X)[0]
        # Convert numpy types to native Python for JSON serialization
        pred = pred.item() if hasattr(pred, "item") else pred
        return PredictionOutput(prediction=pred)
    except Exception as exc:
        logger.error(f"Prediction error: {{exc}}")
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/batch", response_model=BatchOutput, tags=["Inference"])
async def batch_predict(body: BatchInput):
    """
    Batch prediction — send a list of feature dicts, get back a list of predictions.
    Useful for bulk scoring without calling /predict in a loop.
    """
    _require_model()
    try:
        df    = pd.DataFrame(body.records)
        X     = _prep.transform(df)
        preds = _model.predict(X)
        preds_list = [p.item() if hasattr(p, "item") else p for p in preds]
        return BatchOutput(predictions=preds_list, count=len(preds_list))
    except Exception as exc:
        logger.error(f"Batch prediction error: {{exc}}")
        raise HTTPException(status_code=400, detail=str(exc))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _require_model():
    if not MODEL_LOADED:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model not loaded. "
                "Run: cd src/ml_pipeline && python training.py"
            ),
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
'''


def _frontend_py(scope: dict) -> str:
    return f'''\
"""
Streamlit frontend for {scope["project_name"]}.
"""

import streamlit as st
import requests
import pandas as pd
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="{scope["project_name"]}", layout="wide")

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("MLForge")
st.sidebar.caption("Generated by MLForge — ML SMITHS, OIST Bhopal")
page = st.sidebar.radio("Navigation", ["🔮 Predict", "📦 Batch", "📊 About"])

# ── Header ───────────────────────────────────────────────────────────────────
st.title("{scope["project_name"]}")
st.caption(
    f"**{scope["project_prompt"]}** | "
    "Algorithm: **{scope["primary_algorithm"]}** | "
    "Type: **{scope["problem_type"]}**"
)

# Check backend health
try:
    r = requests.get(f"{{API_BASE}}/health", timeout=2)
    health = r.json()
    if health.get("model_loaded"):
        st.success("✅ Backend connected & model loaded")
    else:
        st.warning("⚠️ Backend connected but model not loaded. Run training.py first.")
except Exception:
    st.error("❌ Backend not reachable. Start it: `python src/backend/main.py`")

st.divider()

# ── Pages ────────────────────────────────────────────────────────────────────

if page == "🔮 Predict":
    st.header("Single Prediction")
    st.info("Enter feature values below and click Predict.")

    with st.form("predict_form"):
        cols = st.columns(2)
        f1 = cols[0].number_input("Feature 1", value=1.0)
        f2 = cols[0].number_input("Feature 2", value=2.0)
        f3 = cols[1].number_input("Feature 3", value=3.0)
        f4 = cols[1].number_input("Feature 4", value=4.0)
        submitted = st.form_submit_button("🔮 Predict", use_container_width=True)

    if submitted:
        payload = {{
            "features": {{
                "feature1": f1,
                "feature2": f2,
                "feature3": f3,
                "feature4": f4,
            }}
        }}
        try:
            r = requests.post(f"{{API_BASE}}/predict", json=payload, timeout=10)
            data = r.json()
            if r.status_code == 200:
                st.success(f"**Prediction:** {{data['prediction']}}")
                st.json(data)
            else:
                st.error(f"Error: {{data.get('detail', 'Unknown error')}}")
        except Exception as exc:
            st.warning(f"Request failed: {{exc}}")

elif page == "📦 Batch":
    st.header("Batch Prediction")
    st.info("Upload a CSV file to get predictions for all rows.")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head(10))
        st.caption(f"{{len(df)}} rows, {{len(df.columns)}} columns")

        if st.button("Run Batch Prediction"):
            records = df.to_dict(orient="records")
            try:
                r = requests.post(
                    f"{{API_BASE}}/batch",
                    json={{"records": records}},
                    timeout=30,
                )
                data = r.json()
                if r.status_code == 200:
                    df["prediction"] = data["predictions"]
                    st.success(f"Got {{data['count']}} predictions!")
                    st.dataframe(df)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download Results",
                        csv,
                        file_name="predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(data.get("detail", "Unknown error"))
            except Exception as exc:
                st.warning(f"Request failed: {{exc}}")

else:
    st.header("About This Project")
    st.markdown(f"""
| Field | Value |
|---|---|
| Problem | {scope["project_prompt"]} |
| Type | {scope["problem_type"]} |
| Algorithm | {scope["primary_algorithm"]} |
| Libraries | {scope["libraries_str"]} |
| Preprocessing | {scope["preprocessing_str"]} |
| Analysis Source | {scope["source"]} |
""")
    st.info("{scope["explanation"]}")
    st.markdown("---")
    st.caption("Generated with **MLForge** — ML SMITHS, OIST Bhopal")
'''


def _sample_csv(is_regression: bool, is_clustering: bool, n: int = 150) -> str:
    """Generate a synthetic but realistic-looking CSV."""
    rng = random.Random(42)
    rows = ["feature1,feature2,feature3,feature4,target"]
    for _ in range(n):
        f1 = round(rng.gauss(50, 10), 2)
        f2 = round(rng.gauss(20, 5), 2)
        f3 = round(rng.uniform(0, 100), 2)
        f4 = round(rng.gauss(5, 2), 2)
        if is_regression:
            target = round(f1 * 0.3 + f2 * 0.5 + rng.gauss(0, 2), 2)
        elif is_clustering:
            target = rng.randint(0, 2)  # 3 clusters
        else:
            target = 1 if (f1 + f2 > 70 + rng.gauss(0, 5)) else 0
        rows.append(f"{f1},{f2},{f3},{f4},{target}")
    return "\n".join(rows) + "\n"


def _requirements(analysis: dict) -> str:
    libs = analysis.get("libraries", [])
    # Always include these core deps
    core = [
        "pandas>=2.0",
        "numpy>=1.24",
        "scikit-learn>=1.3",
        "xgboost>=2.0",
        "fastapi>=0.109",
        "uvicorn[standard]>=0.27",
        "streamlit>=1.31",
        "joblib>=1.3",
        "pydantic>=2.0",
        "requests>=2.31",
        "python-dotenv>=1.0",
        "pytest>=7.0",
    ]
    return "\n".join(core) + "\n"


def _dockerfile() -> str:
    return '''\
# Multi-stage isn't needed here since we\'re not compiling anything,
# but we use slim to keep the image small.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first — Docker layer caching means this only
# re-runs when requirements.txt changes, not on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose both the API and Streamlit ports
EXPOSE 8000 8501

# Default: run the backend. Override with docker-compose for frontend.
CMD ["python", "src/backend/main.py"]
'''


def _compose() -> str:
    return '''\
version: "3.8"

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./src:/app/src      # hot-reload code changes without rebuild
      - ./data:/app/data

  frontend:
    build: .
    ports:
      - "8501:8501"
    command: streamlit run src/frontend/app.py --server.address=0.0.0.0
    depends_on:
      - backend
    environment:
      - PYTHONUNBUFFERED=1
'''


def _gitignore() -> str:
    return '''\
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
dist/
build/
.eggs/

# ML artifacts — never commit trained models to git (use DVC instead)
*.joblib
*.pkl
*.h5
*.pt

# Secrets
.env
*.key

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp

# Virtual environments
venv/
.venv/
env/
'''


def _env_example() -> str:
    return '''\
# Copy this file to .env and fill in your values.
# Never commit .env to git — it\'s in .gitignore.

# Add any secrets your project needs, e.g.:
# DATABASE_URL=postgresql://user:pass@localhost/mydb
# API_KEY=your-key-here
'''


def _ci_yml() -> str:
    return '''\
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
'''


def _readme(scope: dict) -> str:
    return f'''\
# {scope["project_name"]}

> {scope["project_prompt"]}

Generated with **[MLForge](https://github.com/mlsmiths/mlforge)** — ML SMITHS, OIST Bhopal

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
cd src/ml_pipeline
python training.py
cd ../..

# 3. Start the API
python src/backend/main.py
# → API docs at http://localhost:8000/docs

# 4. Start the frontend (new terminal)
streamlit run src/frontend/app.py
# → UI at http://localhost:8501
```

## API Usage

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d \'{{"features": {{"feature1": 1.0, "feature2": 2.0, "feature3": 3.0, "feature4": 4.0}}}}\'
```

## Project Info

| Field | Value |
|---|---|
| Problem Type | {scope["problem_type"]} |
| Algorithm | {scope["primary_algorithm"]} |
| Libraries | {scope["libraries_str"]} |
| Preprocessing | {scope["preprocessing_str"]} |

## Structure

```
.
├── data/
│   ├── raw/            # Put your CSV data here
│   └── processed/      # Preprocessed data (auto-generated)
├── src/
│   ├── ml_pipeline/
│   │   ├── preprocessing.py   # Data cleaning & feature engineering
│   │   ├── training.py        # Model training & saving
│   │   └── evaluation.py      # Performance metrics & reports
│   ├── backend/
│   │   └── main.py            # FastAPI REST API
│   └── frontend/
│       └── app.py             # Streamlit dashboard
├── tests/                     # pytest test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Docker

```bash
docker-compose up --build
```
'''


def _architecture_md(scope: dict) -> str:
    return f'''\
# Architecture — {scope["project_name"]}

## Problem Statement

{scope["project_prompt"]}

**Problem Type**: {scope["problem_type"]}  
**Algorithm**: {scope["primary_algorithm"]}

## Why {scope["primary_algorithm"]}?

{scope["explanation"]}

## Data Flow

```
CSV Input
  → DataPreprocessor.fit_transform()
      → Fill missing values (median for numeric, mode for categorical)
      → StandardScaler (normalize numeric features)
      → LabelEncoder (encode categorical features)
  → ModelTrainer.train()
      → Train/test split (80/20)
      → Fit {scope["primary_algorithm"]} model
      → Evaluate on test set
      → Save model.joblib + preprocessor.joblib
  → FastAPI /predict endpoint
      → Load model.joblib + preprocessor.joblib
      → DataPreprocessor.transform() (uses fitted scalers)
      → model.predict()
      → Return JSON response
```

## Component Responsibilities

| Component | File | Responsibility |
|---|---|---|
| Preprocessor | `src/ml_pipeline/preprocessing.py` | Feature engineering, scaling, encoding |
| Trainer | `src/ml_pipeline/training.py` | Model fitting, evaluation, serialization |
| Evaluator | `src/ml_pipeline/evaluation.py` | Detailed performance reporting |
| API | `src/backend/main.py` | REST interface for model inference |
| UI | `src/frontend/app.py` | Interactive prediction dashboard |

## Preprocessing Pipeline

{chr(10).join(f"- **{step}**" for step in scope["preprocessing_steps"])}

## Scalability Notes

- The model is saved as a `.joblib` file and loaded once at API startup.
  This means prediction latency is just the inference time (~1-5ms for tree models).
- For high traffic, deploy behind a load balancer with multiple uvicorn workers:
  `uvicorn src.backend.main:app --workers 4`
- For very large datasets, consider incremental learning or mini-batch training.
'''


def _health_json(scope: dict) -> str:
    import json
    return json.dumps({
        "projectName":     scope["project_name"],
        "algorithm":       scope["primary_algorithm"],
        "problemType":     scope["problem_type"],
        "scores": {
            "scalability":     8,
            "maintainability": 9,
            "deployability":   8,
        },
        "recommendations": [
            "Add input validation for edge cases (nulls, out-of-range values)",
            "Add model monitoring / drift detection in production",
            "Pin dependency versions for reproducibility",
        ],
        "generatedBy": "MLForge v1.0.0 — ML SMITHS, OIST Bhopal",
    }, indent=2) + "\n"


def _test_preprocessing() -> str:
    return '''\
"""Tests for the DataPreprocessor."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/ml_pipeline"))

import pytest
import pandas as pd
import numpy as np
from preprocessing import DataPreprocessor


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "num1": [1.0, 2.0, np.nan, 4.0],
        "num2": [10.0, 20.0, 30.0, 40.0],
        "cat1": ["a", "b", "a", np.nan],
    })


def test_fit_transform_no_crash(sample_df):
    proc = DataPreprocessor()
    result = proc.fit_transform(sample_df)
    assert result.shape == sample_df.shape


def test_missing_values_filled(sample_df):
    proc = DataPreprocessor()
    result = proc.fit_transform(sample_df)
    assert not result.isnull().any().any(), "No nulls should remain after fit_transform"


def test_transform_without_fit_raises(sample_df):
    proc = DataPreprocessor()
    with pytest.raises(RuntimeError):
        proc.transform(sample_df)


def test_transform_after_fit(sample_df):
    proc = DataPreprocessor()
    proc.fit_transform(sample_df)
    new_data = pd.DataFrame({
        "num1": [5.0],
        "num2": [50.0],
        "cat1": ["b"],
    })
    result = proc.transform(new_data)
    assert result.shape[0] == 1
'''


def _test_model(scope: dict) -> str:
    return f'''\
"""Tests for ModelTrainer."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/ml_pipeline"))

import pytest
import pandas as pd
import numpy as np
from training import ModelTrainer


@pytest.fixture
def training_data():
    np.random.seed(42)
    n = 100
    X = pd.DataFrame({{
        "feature1": np.random.normal(50, 10, n),
        "feature2": np.random.normal(20, 5, n),
        "feature3": np.random.uniform(0, 100, n),
        "feature4": np.random.normal(5, 2, n),
    }})
    y = pd.Series(np.random.randint(0, 2, n))
    return X, y


def test_trainer_initializes():
    trainer = ModelTrainer()
    assert trainer.model is not None
    assert trainer.preprocessor is not None


def test_train_returns_score(training_data):
    X, y = training_data
    trainer = ModelTrainer()
    score = trainer.train(X, y)
    assert isinstance(score, float), "Score must be a float"
    assert 0.0 <= score <= 1.0, "Score should be between 0 and 1"


def test_predict_after_train(training_data):
    X, y = training_data
    trainer = ModelTrainer()
    trainer.train(X, y)
    preds = trainer.predict(X.head(5))
    assert len(preds) == 5
'''


def _test_api(scope: dict) -> str:
    return '''\
"""Tests for the FastAPI backend."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import pytest
from fastapi.testclient import TestClient

# Import the app — model may not be loaded in CI, that\'s fine
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_predict_without_model():
    """When the model isn\'t loaded, /predict should return 503, not crash."""
    response = client.post("/predict", json={"features": {"f1": 1.0}})
    # Either 200 (model loaded) or 503 (model not loaded) — both are correct
    assert response.status_code in (200, 503)


def test_predict_bad_payload():
    """Missing 'features' key should return 422 (validation error)."""
    response = client.post("/predict", json={"wrong_key": {}})
    assert response.status_code == 422
'''


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_dirs(root: Path, dirs: list[str]) -> None:
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _git_init(root: Path) -> None:
    try:
        subprocess.run(["git", "init"], cwd=root, capture_output=True, check=False)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial commit by MLForge"],
            cwd=root, capture_output=True, check=False,
        )
    except FileNotFoundError:
        pass  # git not installed — skip silently


def _sanitize_name(prompt: str) -> str:
    """Convert a prompt string to a valid directory name."""
    name = re.sub(r"[^a-z0-9 ]", " ", prompt.lower())
    name = re.sub(r"\s+", "_", name.strip())
    return (name.strip("_") or "ml_project")[:50]  # cap length
