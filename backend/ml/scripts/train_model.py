"""Train fuel consumption prediction model."""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from ml.src.features import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET,
    engineer_features,
)
from ml.src.preprocessing import build_preprocessor


def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true.clip(lower=0.01))) * 100


def train():
    # Load data
    df = pd.read_csv("ml/data/synthetic_trips.csv")
    print(f"Loaded {len(df)} records")

    # Feature engineering
    df = engineer_features(df)

    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols]
    y = df[TARGET]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    preprocessor = build_preprocessor()

    # Define models
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
    }

    results = {}
    best_model_name = None
    best_r2 = -float("inf")
    best_pipeline = None

    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training: {name}")

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = mean_absolute_percentage_error(y_test, y_pred)

        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="r2")

        results[name] = {
            "r2": round(r2, 4),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "mape": round(mape, 2),
            "cv_r2_mean": round(cv_scores.mean(), 4),
            "cv_r2_std": round(cv_scores.std(), 4),
        }

        print(f"  R2:   {r2:.4f}")
        print(f"  MAE:  {mae:.4f} L")
        print(f"  RMSE: {rmse:.4f} L")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipeline = pipeline

    # Save best model
    print(f"\n{'='*50}")
    print(f"Best model: {best_model_name} (R2 = {best_r2:.4f})")

    os.makedirs("ml/models", exist_ok=True)
    model_path = "ml/models/fuel_consumption_model.joblib"
    joblib.dump(best_pipeline, model_path)
    print(f"Saved model to {model_path}")

    # Save metadata
    metadata = {
        "best_model": best_model_name,
        "metrics": results[best_model_name],
        "all_results": results,
        "features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
        },
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    metadata_path = "ml/models/fuel_consumption_model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_path}")

    # Model comparison summary
    print(f"\n{'='*50}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*50}")
    print(f"{'Model':<25} {'R2':>8} {'MAE':>8} {'RMSE':>8} {'MAPE':>8}")
    print("-" * 60)
    for name, metrics in results.items():
        marker = " <-- best" if name == best_model_name else ""
        print(f"{name:<25} {metrics['r2']:>8.4f} {metrics['mae']:>8.4f} {metrics['rmse']:>8.4f} {metrics['mape']:>7.2f}%{marker}")

    return best_pipeline, results


if __name__ == "__main__":
    train()
