from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(exist_ok=True)


def train_regressor(features: np.ndarray, target: np.ndarray, name: str) -> dict:
    split = int(len(features) * 0.8)
    if split < 10 or len(features) - split < 2:
        raise ValueError("Không đủ dữ liệu cho tập train và tập test")
    model = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
    model.fit(features[:split], target[:split])
    predictions = model.predict(features[split:])
    mae = float(mean_absolute_error(target[split:], predictions))
    joblib.dump(model, MODEL_DIR / f"{name}.joblib")
    return {"train_rows": split, "test_rows": len(features) - split, "mae": mae}


def train_forecast_models(features: np.ndarray, targets: dict[str, np.ndarray]) -> dict:
    split = int(len(features) * 0.8)
    if split < 50 or len(features) - split < 20:
        raise ValueError("Không đủ dữ liệu cho tập train và tập test")

    metrics = {"train_rows": split, "test_rows": len(features) - split, "targets": {}}
    for name, target in targets.items():
        if name == "storm":
            model = RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
            model.fit(features[:split], target[:split])
            predictions = model.predict(features[split:])
            metrics["targets"][name] = {
                "accuracy": float(accuracy_score(target[split:], predictions)),
                "f1": float(f1_score(target[split:], predictions, zero_division=0)),
            }
        else:
            model = RandomForestRegressor(
                n_estimators=300,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
            model.fit(features[:split], target[:split])
            predictions = model.predict(features[split:])
            metrics["targets"][name] = {
                "mae": float(mean_absolute_error(target[split:], predictions)),
                "rmse": float(np.sqrt(mean_squared_error(target[split:], predictions))),
            }
        joblib.dump(model, MODEL_DIR / f"weather_{name}.joblib")
    return metrics
