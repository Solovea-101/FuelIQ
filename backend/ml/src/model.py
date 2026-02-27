"""Model wrapper for serving predictions."""
import joblib
import pandas as pd
import numpy as np

from ml.src.features import engineer_features, NUMERICAL_FEATURES, CATEGORICAL_FEATURES


class FuelConsumptionModel:
    def __init__(self, model_path: str):
        self.pipeline = joblib.load(model_path)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        features = engineer_features(features)
        feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
        X = features[feature_cols]
        return self.pipeline.predict(X)
