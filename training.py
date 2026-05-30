import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from preprocessing import DataPreprocessor


class ModelTrainer:
    def __init__(self):
        self.model = XGBClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.preprocessor = DataPreprocessor()

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        X_proc = self.preprocessor.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_proc, y, test_size=test_size, random_state=42
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        score = accuracy_score(y_test, y_pred)
        print(f"  Accuracy: {score:.4f}")
        return score

    def save(self, path: str = "model.joblib"):
        joblib.dump(self.model, path)
        joblib.dump(self.preprocessor, "preprocessor.joblib")
        print(f"  Model saved → {path}")

    def predict(self, X: pd.DataFrame):
        X_proc = self.preprocessor.transform(X)
        return self.model.predict(X_proc)


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "../../data/raw/sample_data.csv")

    if not os.path.exists(data_path):
        print("Sample data not found — generating synthetic data...")
        rng = np.random.default_rng(42)
        n = 200
        df = pd.DataFrame({
            "feature1": rng.normal(50, 10, n),
            "feature2": rng.normal(20, 5,  n),
            "feature3": rng.uniform(0, 100, n),
            "feature4": rng.normal(5, 2,   n),
            "target":   rng.integers(0, 2, n) if not False else rng.normal(100, 20, n),
        })
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
    print("Done!")
