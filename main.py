import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../ml_pipeline"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(
    title="Fraud Detection For Bank Transactions API",
    description="fraud detection for bank transactions",
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
    print(f"[warn] Model not loaded: {e}")


class PredictionInput(BaseModel):
    features: dict


class PredictionOutput(BaseModel):
    prediction: float
    status: str = "success"


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": MODEL_LOADED}


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
